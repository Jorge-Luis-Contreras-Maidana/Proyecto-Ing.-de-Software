"""Acceso a datos de las citas de seguimiento. Aquí vive el SQL."""
from sqlalchemy import select

from app.extensions import db
from app.modules.followup.models.followup import AlertaAsistencia
from app.modules.meetings.models.meetings import Citacion
from app.modules.students.models.guardian_link import EstudianteTutor, Tutor
from app.modules.students.models.students import (
    Estudiante,
    GestionEscolar,
    Profesor,
)


class MeetingsRepository:
    # ---------- gestión escolar ----------
    def active_gestion(self) -> GestionEscolar | None:
        stmt = (
            select(GestionEscolar)
            .where(GestionEscolar.estado == "activa")
            .order_by(GestionEscolar.anio.desc())
            .limit(1)
        )
        return db.session.execute(stmt).scalar_one_or_none()

    # ---------- acceso por fila (RD-02.1) ----------
    def access_condition(self, columna, roles, id_usuario: int, id_gestion: int | None):
        """Condición SQL con los estudiantes visibles para el usuario.

        El personal (dirección y profesorado) ve todas las citas; el tutor solo
        ve las de los estudiantes a su cargo, con el vínculo confirmado por la
        dirección (RD-02.2). None significa "sin restricción".
        """
        if "director" in roles or "profesor" in roles or "tutor" not in roles:
            return None
        hijos = (
            select(EstudianteTutor.id_estudiante)
            .join(Tutor, Tutor.id_tutor == EstudianteTutor.id_tutor)
            .where(Tutor.id_usuario == id_usuario, EstudianteTutor.confirmado.is_(True))
        )
        return columna.in_(hijos)

    # ---------- citas ----------
    def list_citas(self, estado=None, id_estudiante=None, access=None):
        stmt = select(Citacion)
        if access is not None:
            stmt = stmt.where(access)
        if estado:
            stmt = stmt.where(Citacion.estado == estado)
        if id_estudiante:
            stmt = stmt.where(Citacion.id_estudiante == id_estudiante)
        stmt = stmt.order_by(Citacion.fecha_hora.desc(), Citacion.id_citacion.desc())
        return db.session.execute(stmt).scalars().all()

    def get_citacion(self, id_citacion: int) -> Citacion | None:
        return db.session.get(Citacion, id_citacion)

    def add_citacion(self, citacion: Citacion) -> Citacion:
        db.session.add(citacion)
        db.session.flush()
        return citacion

    # ---------- datos relacionados ----------
    def get_estudiante(self, id_estudiante: int) -> Estudiante | None:
        return db.session.get(Estudiante, id_estudiante)

    def get_tutor(self, id_tutor: int) -> Tutor | None:
        return db.session.get(Tutor, id_tutor)

    def get_profesor(self, id_profesor: int) -> Profesor | None:
        return db.session.get(Profesor, id_profesor)

    def get_alerta(self, id_alerta: int) -> AlertaAsistencia | None:
        return db.session.get(AlertaAsistencia, id_alerta)

    def estudiante_visible(self, id_estudiante: int, access) -> bool:
        stmt = select(Estudiante.id_estudiante).where(Estudiante.id_estudiante == id_estudiante)
        if access is not None:
            stmt = stmt.where(access)
        return db.session.execute(stmt).first() is not None
