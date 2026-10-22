"""Reglas de las justificaciones de ausencia. No usa Flask ni escribe SQL."""
from sqlalchemy import select

from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.core.errors.exceptions import InvalidData, NotFound
from app.extensions import db
from app.modules.justifications.repositories.justifications_repository import JustificationsRepository
from app.modules.students.models.guardian_link import Tutor

# Estados que puede asignar la dirección (los mismos que admite la tabla).
ESTADOS_REVISION = ("pendiente", "avisada", "justificada", "no_justificada", "requiere_informacion")

# Roles que pueden ver el listado completo.
PERSONAL = ("director", "profesor")


class JustificationsService:
    def __init__(self, repo=None):
        self.repo = repo or JustificationsRepository()

    @staticmethod
    def _tutor_del_usuario(id_usuario: int) -> int | None:
        stmt = select(Tutor.id_tutor).where(Tutor.id_usuario == id_usuario)
        return db.session.execute(stmt).scalar_one_or_none()

    def list(self, principal, estado=None, id_estudiante=None):
        """Listado. El tutor solo ve las justificaciones de sus propios estudiantes."""
        if "director" in principal.roles or "profesor" in principal.roles:
            return self.repo.list(estado, id_estudiante)
        id_tutor = self._tutor_del_usuario(principal.id_usuario)
        if id_tutor is None:
            return []
        return self.repo.list(estado, id_estudiante, id_tutor)

    def crear(self, principal, id_estudiante: int, fecha_inicio, fecha_fin, motivo: str, documento: str | None = None):
        """El tutor solicita la justificación de una ausencia."""
        id_tutor = self._tutor_del_usuario(principal.id_usuario)
        if id_tutor is None:
            raise InvalidData(
                "Su cuenta no está vinculada a un tutor.",
                "Comuníquese con la dirección de la unidad educativa.",
            )
        if fecha_fin < fecha_inicio:
            raise InvalidData(
                "La fecha final no puede ser anterior a la inicial.",
                "Corrija el rango de fechas e intente nuevamente.",
            )
        if motivo.strip() == "":
            raise InvalidData("El motivo no puede estar vacío.", "Describa el motivo de la ausencia.")

        from app.modules.justifications.models.justification import JustificacionAusencia

        with unit_of_work():
            justificacion = self.repo.add(
                JustificacionAusencia(
                    id_estudiante=id_estudiante,
                    id_tutor=id_tutor,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    motivo_declarado=motivo,
                    documento_referencia=documento,
                    solicitada_en=clock.now(),
                    estado="pendiente",
                )
            )
        return justificacion

    def revisar(self, principal, id_justificacion: int, estado: str, comentario: str | None = None):
        """La dirección revisa la justificación y, si la acepta, justifica la asistencia."""
        justificacion = self.repo.get(id_justificacion)
        if justificacion is None:
            raise NotFound("No se encontró la justificación.", "Verifique la justificación o regrese al inicio.")
        if estado not in ESTADOS_REVISION:
            raise InvalidData("El estado indicado no es válido.", "Seleccione un estado de la lista.")

        with unit_of_work():
            justificacion.estado = estado
            justificacion.revisada_por = principal.id_usuario
            justificacion.revisada_en = clock.now()
            justificacion.comentario_revision = comentario
            if estado == "justificada":
                self._justificar_asistencias(justificacion)
        return justificacion

    def _justificar_asistencias(self, justificacion) -> None:
        """Marca como justificadas las asistencias del estudiante en el rango de fechas."""
        for asistencia in self.repo.attendance_of_day(justificacion.id_estudiante, justificacion.fecha_inicio):
            asistencia.estado = "justificada"
            asistencia.hora_ingreso = None
            asistencia.metodo_ingreso = "no_aplica"
            asistencia.id_justificacion = justificacion.id_justificacion
