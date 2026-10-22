"""Acceso a datos de las alertas de seguimiento. Aquí vive el SQL."""
from datetime import date

from sqlalchemy import select

from app.extensions import db
from app.modules.attendance.models.attendance import RegistroAsistencia, SesionClase
from app.modules.auth.models.auth import Usuario
from app.modules.followup.models.followup import AlertaAsistencia
from app.modules.students.models.guardian_link import EstudianteTutor, Tutor
from app.modules.students.models.students import (
    AsignacionDocente,
    Curso,
    Estudiante,
    GestionEscolar,
)

# Estados en los que la alerta sigue viva: una alerta viva no se duplica (RF-05).
ESTADOS_VIVOS = ("abierta", "en_seguimiento")


class FollowupRepository:
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
        """Condición SQL con los estudiantes que el usuario puede ver.

        El personal (dirección y profesorado) ve todas las alertas; el tutor
        solo ve las de los estudiantes a su cargo, con el vínculo confirmado por
        la dirección (RD-02.2). None significa "sin restricción".
        """
        if "director" in roles or "profesor" in roles or "tutor" not in roles:
            return None
        hijos = (
            select(EstudianteTutor.id_estudiante)
            .join(Tutor, Tutor.id_tutor == EstudianteTutor.id_tutor)
            .where(Tutor.id_usuario == id_usuario, EstudianteTutor.confirmado.is_(True))
        )
        return columna.in_(hijos)

    # ---------- alertas ----------
    def list_alertas(self, estado=None, id_estudiante=None, id_curso=None, access=None):
        stmt = select(AlertaAsistencia)
        if access is not None:
            stmt = stmt.where(access)
        if estado:
            stmt = stmt.where(AlertaAsistencia.estado == estado)
        if id_estudiante:
            stmt = stmt.where(AlertaAsistencia.id_estudiante == id_estudiante)
        if id_curso:
            stmt = stmt.where(AlertaAsistencia.id_curso == id_curso)
        stmt = stmt.order_by(
            AlertaAsistencia.generada_en.desc(),
            AlertaAsistencia.id_alerta.desc(),
        )
        return db.session.execute(stmt).scalars().all()

    def get_alerta(self, id_alerta: int) -> AlertaAsistencia | None:
        return db.session.get(AlertaAsistencia, id_alerta)

    def add_alerta(self, alerta: AlertaAsistencia) -> AlertaAsistencia:
        db.session.add(alerta)
        db.session.flush()
        return alerta

    def alertas_vivas(self) -> set[tuple[int, str]]:
        """Pares (estudiante, tipo) con una alerta abierta o en seguimiento."""
        stmt = select(AlertaAsistencia.id_estudiante, AlertaAsistencia.tipo).where(
            AlertaAsistencia.estado.in_(ESTADOS_VIVOS)
        )
        return set(db.session.execute(stmt).all())

    # ---------- estudiantes y cursos ----------
    def get_estudiante(self, id_estudiante: int) -> Estudiante | None:
        return db.session.get(Estudiante, id_estudiante)

    def get_curso(self, id_curso: int) -> Curso | None:
        return db.session.get(Curso, id_curso)

    def estudiante_visible(self, id_estudiante: int, access) -> bool:
        stmt = select(Estudiante.id_estudiante).where(Estudiante.id_estudiante == id_estudiante)
        if access is not None:
            stmt = stmt.where(access)
        return db.session.execute(stmt).first() is not None

    def existe_usuario(self, id_usuario: int) -> bool:
        """True si el identificador corresponde a un usuario del sistema."""
        stmt = select(Usuario.id_usuario).where(Usuario.id_usuario == id_usuario)
        return db.session.execute(stmt).first() is not None

    # ---------- detección de patrones ----------
    def asistencias_de_gestion(self, id_gestion: int, hasta: date | None = None):
        """Asistencias de la gestión: estudiante, curso, fecha, hora y estado."""
        stmt = (
            select(
                RegistroAsistencia.id_estudiante,
                AsignacionDocente.id_curso,
                SesionClase.fecha,
                SesionClase.hora_inicio_prevista,
                RegistroAsistencia.estado,
            )
            .join(SesionClase, SesionClase.id_sesion_clase == RegistroAsistencia.id_sesion_clase)
            .join(AsignacionDocente, AsignacionDocente.id_asignacion == SesionClase.id_asignacion)
            .where(AsignacionDocente.id_gestion == id_gestion)
        )
        if hasta is not None:
            stmt = stmt.where(SesionClase.fecha <= hasta)
        stmt = stmt.order_by(
            RegistroAsistencia.id_estudiante,
            AsignacionDocente.id_curso,
            SesionClase.fecha,
            SesionClase.hora_inicio_prevista,
        )
        return db.session.execute(stmt).all()
