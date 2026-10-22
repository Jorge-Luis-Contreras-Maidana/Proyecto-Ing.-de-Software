"""Reglas de negocio del seguimiento de asistencia. No usa Flask ni escribe SQL."""
import logging

from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.core.errors.exceptions import InvalidData, NotFound, PermissionDenied
from app.modules.followup.models.followup import AlertaAsistencia
from app.modules.followup.repositories.followup_repository import FollowupRepository
from app.modules.followup.services.pattern_detector import PatternDetector
from app.modules.students.models.students import Estudiante

log = logging.getLogger(__name__)

# Tipos y estados que admite la tabla alertas_asistencia.
TIPOS_ALERTA = (
    "ausencias_consecutivas",
    "tardanzas_reiteradas",
    "porcentaje_ausencia",
    "otra",
)
ESTADOS_ALERTA = ("abierta", "en_seguimiento", "resuelta", "descartada")
ESTADOS_CERRADOS = ("resuelta", "descartada")

try:  # el servicio de auditoría puede estar todavía en construcción
    from app.modules.audit.services.audit_logger import AuditLogger
except ImportError:  # pragma: no cover
    AuditLogger = None


def registrar_auditoria(id_usuario, operacion: str, entidad: str, id_registro=None, detalle=None) -> None:
    """Deja rastro en la bitácora; si falla, no interrumpe la operación."""
    if AuditLogger is None:
        return
    try:
        AuditLogger().registrar(
            id_usuario,
            operacion,
            entidad,
            id_registro=None if id_registro is None else str(id_registro),
            detalle=detalle,
        )
    except Exception:  # pragma: no cover - la auditoría nunca debe romper la operación
        log.warning("No se pudo registrar el evento de auditoría %s.", operacion, exc_info=True)


class FollowupService:
    def __init__(self, repo=None, detector=None):
        self.repo = repo or FollowupRepository()
        self.detector = detector or PatternDetector(repo=self.repo)

    # ---------- acceso ----------
    def _access(self, principal, columna):
        """Condición de visibilidad según el rol del usuario (RD-02.1)."""
        gestion = self.repo.active_gestion()
        id_gestion = gestion.id_gestion if gestion else None
        return self.repo.access_condition(columna, principal.roles, principal.id_usuario, id_gestion)

    def _estudiante_visible(self, principal, id_estudiante: int) -> bool:
        access = self._access(principal, Estudiante.id_estudiante)
        return self.repo.estudiante_visible(id_estudiante, access)

    def _alerta_visible(self, principal, id_alerta: int) -> AlertaAsistencia:
        alerta = self.repo.get_alerta(id_alerta)
        if alerta is None:
            raise NotFound(
                "No se encontró la alerta de seguimiento.",
                "Verifique la alerta o regrese al inicio.",
            )
        access = self._access(principal, Estudiante.id_estudiante)
        if access is not None and not self.repo.estudiante_visible(alerta.id_estudiante, access):
            raise NotFound(
                "No se encontró la alerta de seguimiento.",
                "Verifique la alerta o regrese al inicio.",
            )
        return alerta

    # ---------- lectura ----------
    def listar(self, principal, estado=None, id_estudiante=None, id_curso=None):
        """Alertas de seguimiento visibles para el usuario."""
        access = self._access(principal, AlertaAsistencia.id_estudiante)
        alertas = self.repo.list_alertas(estado, id_estudiante, id_curso, access)
        return alertas, len(alertas)

    def obtener(self, principal, id_alerta: int) -> AlertaAsistencia:
        return self._alerta_visible(principal, id_alerta)

    def alertas_de_estudiante(self, principal, id_estudiante: int):
        """Alertas de un estudiante. El tutor solo ve los de sus hijos."""
        if not self._estudiante_visible(principal, id_estudiante):
            raise NotFound(
                "No se encontró el estudiante.",
                "Verifique el estudiante o regrese al inicio.",
            )
        access = self._access(principal, AlertaAsistencia.id_estudiante)
        return self.repo.list_alertas(None, id_estudiante, None, access)

    # ---------- escritura ----------
    def crear(self, principal, id_estudiante: int, id_curso: int, tipo: str, descripcion: str, asignada_a=None):
        """Registra una alerta de seguimiento a mano."""
        if tipo not in TIPOS_ALERTA:
            raise InvalidData("El tipo de alerta no es válido.", "Seleccione un tipo de la lista.")
        if not descripcion or not descripcion.strip():
            raise InvalidData("La descripción de la alerta no puede estar vacía.", "Describa el motivo de la alerta.")
        if self.repo.get_estudiante(id_estudiante) is None:
            raise NotFound("No se encontró el estudiante.", "Verifique el estudiante o regrese al inicio.")
        if self.repo.get_curso(id_curso) is None:
            raise NotFound("El curso indicado no existe.", "Elija un curso de la lista.")
        if not self._estudiante_visible(principal, id_estudiante):
            raise PermissionDenied(
                "No tiene permiso para crear alertas para este estudiante.",
                "Solo puede registrar alertas de los estudiantes a su cargo.",
            )
        if asignada_a is not None and not self.repo.existe_usuario(asignada_a):
            raise NotFound("El usuario asignado no existe.", "Elija a un usuario válido.")

        with unit_of_work():
            alerta = self.repo.add_alerta(
                AlertaAsistencia(
                    id_estudiante=id_estudiante,
                    id_curso=id_curso,
                    tipo=tipo,
                    descripcion=descripcion.strip(),
                    generada_en=clock.now(),
                    estado="abierta",
                    asignada_a=asignada_a,
                )
            )
        registrar_auditoria(
            principal.id_usuario,
            "CREAR_ALERTA",
            "alertas_asistencia",
            alerta.id_alerta,
            f"Alerta de tipo {tipo} para el estudiante {id_estudiante}.",
        )
        return alerta

    def cambiar_estado(self, principal, id_alerta: int, estado: str, observacion: str | None = None):
        """Cambia el estado de una alerta (abierta, en_seguimiento, resuelta o descartada)."""
        if estado not in ESTADOS_ALERTA:
            raise InvalidData("El estado indicado no es válido.", "Seleccione un estado de la lista.")
        alerta = self._alerta_visible(principal, id_alerta)
        with unit_of_work():
            alerta.estado = estado
            if observacion is not None:
                alerta.observacion = observacion
            alerta.resuelta_en = clock.now() if estado in ESTADOS_CERRADOS else None
        registrar_auditoria(
            principal.id_usuario,
            "REVISAR_ALERTA",
            "alertas_asistencia",
            alerta.id_alerta,
            f"Estado de la alerta: {estado}.",
        )
        return alerta

    # ---------- detección automática ----------
    def detectar(self, principal=None):
        """Detecta patrones de inasistencia y crea las alertas que falten.

        Devuelve la lista de alertas creadas y cuántas se omitieron por existir
        ya una alerta viva del mismo tipo y estudiante.
        """
        patrones = self.detector.detectar()
        vivas = self.repo.alertas_vivas()
        creadas = []
        omitidas = 0
        with unit_of_work():
            for patron in patrones:
                clave = (patron.id_estudiante, patron.tipo)
                if clave in vivas:
                    omitidas += 1
                    continue
                vivas.add(clave)
                creada = self.repo.add_alerta(
                    AlertaAsistencia(
                        id_estudiante=patron.id_estudiante,
                        id_curso=patron.id_curso,
                        tipo=patron.tipo,
                        descripcion=patron.descripcion,
                        generada_en=clock.now(),
                        estado="abierta",
                    )
                )
                creadas.append(creada)
        if principal is not None:
            registrar_auditoria(
                principal.id_usuario,
                "DETECTAR_ALERTAS",
                "alertas_asistencia",
                None,
                f"{len(creadas)} alertas generadas y {omitidas} ya existentes.",
            )
        return creadas, omitidas
