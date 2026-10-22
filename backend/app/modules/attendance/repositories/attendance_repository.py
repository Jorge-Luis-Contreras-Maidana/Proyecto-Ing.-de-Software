from datetime import date

from sqlalchemy import and_, func, select

from app.extensions import db
from app.modules.attendance.models.attendance import (
    AvisoInasistenciaDocente,
    RegistroAsistencia,
    RegistroSalida,
    SesionClase,
)
from app.modules.students.models.students import (
    AsignacionDocente,
    Curso,
    Inscripcion,
    Profesor,
)


class AttendanceRepository:
    # ---------- sesiones de clase ----------
    def get_session(self, id_sesion_clase: int) -> SesionClase | None:
        return db.session.get(SesionClase, id_sesion_clase)

    def _session_query(self):
        return (
            select(SesionClase, AsignacionDocente, Curso)
            .join(AsignacionDocente, AsignacionDocente.id_asignacion == SesionClase.id_asignacion)
            .join(Curso, Curso.id_curso == AsignacionDocente.id_curso)
        )

    def sessions_for_student(self, id_estudiante: int, fecha: date) -> list[SesionClase]:
        """Sesiones de la fecha a las que el estudiante puede asistir, ordenadas por hora."""
        cursos = select(Inscripcion.id_curso).where(
            Inscripcion.id_estudiante == id_estudiante,
            Inscripcion.estado == "inscrito",
        )
        stmt = (
            select(SesionClase)
            .join(AsignacionDocente, AsignacionDocente.id_asignacion == SesionClase.id_asignacion)
            .where(
                SesionClase.fecha == fecha,
                AsignacionDocente.id_curso.in_(cursos),
                SesionClase.estado.in_(("programada", "abierta", "cerrada")),
            )
            .order_by(SesionClase.hora_inicio_prevista)
        )
        return list(db.session.execute(stmt).scalars().all())

    def sessions_for_date(self, fecha: date, id_curso: int | None = None, id_profesor: int | None = None):
        stmt = self._session_query().where(SesionClase.fecha == fecha)
        if id_curso is not None:
            stmt = stmt.where(AsignacionDocente.id_curso == id_curso)
        if id_profesor is not None:
            stmt = stmt.where(AsignacionDocente.id_profesor == id_profesor)
        stmt = stmt.order_by(SesionClase.hora_inicio_prevista, Curso.id_curso)
        return db.session.execute(stmt).all()

    def professor_courses(self, id_usuario: int, id_gestion: int | None = None):
        """Cursos en los que el profesor imparte en la gestión indicada."""
        stmt = (
            select(AsignacionDocente.id_curso)
            .join(Profesor, Profesor.id_profesor == AsignacionDocente.id_profesor)
            .where(Profesor.id_usuario == id_usuario)
        )
        if id_gestion is not None:
            stmt = stmt.where(AsignacionDocente.id_gestion == id_gestion)
        return list(db.session.execute(stmt).scalars().all())

    # ---------- asistencias ----------
    def get_asistencia(self, id_sesion_clase: int, id_estudiante: int) -> RegistroAsistencia | None:
        stmt = select(RegistroAsistencia).where(
            RegistroAsistencia.id_sesion_clase == id_sesion_clase,
            RegistroAsistencia.id_estudiante == id_estudiante,
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def add_asistencia(self, asistencia: RegistroAsistencia) -> RegistroAsistencia:
        db.session.add(asistencia)
        db.session.flush()
        return asistencia

    def students_of_session(self, id_sesion_clase: int, id_gestion: int | None = None):
        """Estudiantes inscritos en el curso de la sesión, con su asistencia."""
        sesion = self.get_session(id_sesion_clase)
        if sesion is None:
            return []
        asignacion = db.session.get(AsignacionDocente, sesion.id_asignacion)
        if asignacion is None:
            return []
        stmt = (
            select(Inscripcion.id_estudiante, RegistroAsistencia)
            .outerjoin(
                RegistroAsistencia,
                and_(
                    RegistroAsistencia.id_estudiante == Inscripcion.id_estudiante,
                    RegistroAsistencia.id_sesion_clase == id_sesion_clase,
                ),
            )
            .where(Inscripcion.id_curso == asignacion.id_curso, Inscripcion.estado == "inscrito")
        )
        if id_gestion is not None:
            stmt = stmt.where(Inscripcion.id_gestion == id_gestion)
        return db.session.execute(stmt).all()

    def attendance_history(self, id_estudiante: int, desde: date | None = None, hasta: date | None = None):
        stmt = (
            select(RegistroAsistencia, SesionClase)
            .join(SesionClase, SesionClase.id_sesion_clase == RegistroAsistencia.id_sesion_clase)
            .where(RegistroAsistencia.id_estudiante == id_estudiante)
        )
        if desde is not None:
            stmt = stmt.where(SesionClase.fecha >= desde)
        if hasta is not None:
            stmt = stmt.where(SesionClase.fecha <= hasta)
        stmt = stmt.order_by(SesionClase.fecha.desc(), SesionClase.hora_inicio_prevista.desc())
        return db.session.execute(stmt).all()

    # ---------- conteos ----------
    def count_by_state(self, id_sesion_clase: int) -> dict:
        stmt = (
            select(RegistroAsistencia.estado, func.count(RegistroAsistencia.id_asistencia))
            .where(RegistroAsistencia.id_sesion_clase == id_sesion_clase)
            .group_by(RegistroAsistencia.estado)
        )
        return dict(db.session.execute(stmt).all())

    # ---------- salidas ----------
    def salida_of_student(self, id_estudiante: int, fecha: date) -> RegistroSalida | None:
        stmt = select(RegistroSalida).where(
            RegistroSalida.id_estudiante == id_estudiante,
            RegistroSalida.fecha_salida == fecha,
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def add_salida(self, salida: RegistroSalida) -> RegistroSalida:
        db.session.add(salida)
        db.session.flush()
        return salida

    # ---------- avisos de inasistencia docente ----------
    def add_aviso_docente(self, aviso: AvisoInasistenciaDocente) -> AvisoInasistenciaDocente:
        db.session.add(aviso)
        db.session.flush()
        return aviso

    def avisos_docente(self, id_profesor: int | None = None):
        stmt = select(AvisoInasistenciaDocente)
        if id_profesor is not None:
            stmt = stmt.where(AvisoInasistenciaDocente.id_profesor == id_profesor)
        stmt = stmt.order_by(AvisoInasistenciaDocente.fecha_afectada.desc())
        return db.session.execute(stmt).scalars().all()
