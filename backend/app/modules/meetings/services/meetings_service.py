"""Reglas de negocio de las citas de seguimiento. No usa Flask ni escribe SQL."""
import logging

from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.core.errors.exceptions import InvalidData, NotFound, PermissionDenied
from app.modules.meetings.models.meetings import Citacion
from app.modules.meetings.repositories.meetings_repository import MeetingsRepository
from app.modules.students.models.students import Estudiante

log = logging.getLogger(__name__)

# Estados que admite la tabla citaciones.
ESTADOS_CITACION = ("programada", "confirmada", "realizada", "cancelada", "reprogramada")
ESTADOS_CERRADOS = ("realizada", "cancelada")

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


class MeetingsService:
    def __init__(self, repo=None):
        self.repo = repo or MeetingsRepository()

    # ---------- acceso ----------
    def _access(self, principal, columna):
        gestion = self.repo.active_gestion()
        id_gestion = gestion.id_gestion if gestion else None
        return self.repo.access_condition(columna, principal.roles, principal.id_usuario, id_gestion)

    def _citacion_visible(self, principal, id_citacion: int) -> Citacion:
        citacion = self.repo.get_citacion(id_citacion)
        if citacion is None:
            raise NotFound("No se encontró la cita.", "Verifique la cita o regrese al inicio.")
        access = self._access(principal, Estudiante.id_estudiante)
        if access is not None and not self.repo.estudiante_visible(citacion.id_estudiante, access):
            raise NotFound("No se encontró la cita.", "Verifique la cita o regrese al inicio.")
        return citacion

    # ---------- lectura ----------
    def listar(self, principal, estado=None, id_estudiante=None):
        """Citas de seguimiento visibles para el usuario."""
        access = self._access(principal, Citacion.id_estudiante)
        citas = self.repo.list_citas(estado, id_estudiante, access)
        return citas, len(citas)

    def obtener(self, principal, id_citacion: int) -> Citacion:
        return self._citacion_visible(principal, id_citacion)

    # ---------- escritura ----------
    def crear(
        self,
        principal,
        id_estudiante: int,
        id_tutor: int,
        id_profesor: int,
        id_alerta: int | None,
        fecha_hora,
        motivo: str,
        observaciones: str | None = None,
    ) -> Citacion:
        """Crea una cita entre el profesor y el tutor para revisar a un estudiante."""
        if not motivo or not motivo.strip():
            raise InvalidData("El motivo de la cita no puede estar vacío.", "Describa el motivo de la cita.")
        if fecha_hora is None:
            raise InvalidData("Indique la fecha y hora de la cita.", "Elija la fecha y hora de la reunión.")
        if self.repo.get_estudiante(id_estudiante) is None:
            raise NotFound("No se encontró el estudiante.", "Verifique el estudiante o regrese al inicio.")
        if self.repo.get_tutor(id_tutor) is None:
            raise NotFound("No se encontró el tutor.", "Elija un tutor de la lista.")
        if self.repo.get_profesor(id_profesor) is None:
            raise NotFound("No se encontró el profesor.", "Elija un profesor de la lista.")
        if id_alerta is not None:
            alerta = self.repo.get_alerta(id_alerta)
            if alerta is None:
                raise NotFound("No se encontró la alerta de seguimiento.", "Verifique la alerta o regístrela de nuevo.")
            if alerta.id_estudiante != id_estudiante:
                raise InvalidData(
                    "La alerta de seguimiento no corresponde al estudiante indicado.",
                    "Elija la alerta del mismo estudiante.",
                )
        access = self._access(principal, Estudiante.id_estudiante)
        if access is not None and not self.repo.estudiante_visible(id_estudiante, access):
            raise PermissionDenied(
                "No tiene permiso para citar a este estudiante.",
                "Solo puede citar a los estudiantes a su cargo.",
            )

        with unit_of_work():
            citacion = self.repo.add_citacion(
                Citacion(
                    id_estudiante=id_estudiante,
                    id_tutor=id_tutor,
                    id_profesor=id_profesor,
                    id_alerta=id_alerta,
                    fecha_hora=fecha_hora,
                    motivo=motivo.strip(),
                    estado="programada",
                    creada_en=clock.now(),
                    observaciones=observaciones,
                )
            )
        registrar_auditoria(
            principal.id_usuario,
            "CREAR_CITACION",
            "citaciones",
            citacion.id_citacion,
            f"Cita programada para el estudiante {id_estudiante}.",
        )
        return citacion

    def cambiar_estado(self, principal, id_citacion: int, estado: str, observaciones: str | None = None) -> Citacion:
        """Cambia el estado de una cita."""
        if estado not in ESTADOS_CITACION:
            raise InvalidData("El estado indicado no es válido.", "Seleccione un estado de la lista.")
        citacion = self._citacion_visible(principal, id_citacion)
        with unit_of_work():
            citacion.estado = estado
            if observaciones is not None:
                citacion.observaciones = observaciones
        registrar_auditoria(
            principal.id_usuario,
            "REVISAR_CITACION",
            "citaciones",
            citacion.id_citacion,
            f"Estado de la cita: {estado}.",
        )
        return citacion
