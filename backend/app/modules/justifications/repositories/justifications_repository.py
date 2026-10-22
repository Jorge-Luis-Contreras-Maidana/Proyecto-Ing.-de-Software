from sqlalchemy import select

from app.extensions import db
from app.modules.justifications.models.justification import JustificacionAusencia


class JustificationsRepository:
    def get(self, id_justificacion: int) -> JustificacionAusencia | None:
        return db.session.get(JustificacionAusencia, id_justificacion)

    def list(self, estado: str | None = None, id_estudiante: int | None = None, id_tutor: int | None = None):
        stmt = select(JustificacionAusencia)
        if estado:
            stmt = stmt.where(JustificacionAusencia.estado == estado)
        if id_estudiante:
            stmt = stmt.where(JustificacionAusencia.id_estudiante == id_estudiante)
        if id_tutor:
            stmt = stmt.where(JustificacionAusencia.id_tutor == id_tutor)
        stmt = stmt.order_by(JustificacionAusencia.solicitada_en.desc())
        return db.session.execute(stmt).scalars().all()

    def add(self, justificacion: JustificacionAusencia) -> JustificacionAusencia:
        db.session.add(justificacion)
        db.session.flush()
        return justificacion

    def attendance_of_day(self, id_estudiante: int, fecha):
        """Asistencia del estudiante en la fecha de la justificación."""
        from app.modules.attendance.models.attendance import RegistroAsistencia, SesionClase

        stmt = (
            select(RegistroAsistencia)
            .join(SesionClase, SesionClase.id_sesion_clase == RegistroAsistencia.id_sesion_clase)
            .where(
                RegistroAsistencia.id_estudiante == id_estudiante,
                SesionClase.fecha == fecha,
            )
            .order_by(SesionClase.hora_inicio_prevista)
        )
        return db.session.execute(stmt).scalars().all()
