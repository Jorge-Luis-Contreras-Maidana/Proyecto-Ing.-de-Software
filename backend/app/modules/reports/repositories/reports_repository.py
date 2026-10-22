"""Acceso a datos para los reportes de asistencia. Aquí vive el SQL."""
from datetime import date

from sqlalchemy import case, func, select, text

from app.core.database.base import SCHEMA
from app.extensions import db
from app.modules.attendance.models.attendance import RegistroAsistencia, SesionClase
from app.modules.students.models.guardian_link import EstudianteTutor, Tutor
from app.modules.students.models.students import (
    AsignacionDocente,
    Curso,
    Estudiante,
    GestionEscolar,
    Inscripcion,
    Profesor,
)

# La vista diaria resume las asistencias por estudiante y fecha (no es una tabla).
VISTA_DIARIA = text(
    f"""
    SELECT v.id_estudiante,
           e.codigo_estudiante,
           e.nombres,
           e.apellidos,
           v.fecha,
           v.total_clases,
           v.presentes,
           v.tardanzas,
           v.ausencias,
           v.justificadas,
           v.pendientes,
           v.primer_ingreso,
           v.ultima_salida
    FROM {SCHEMA}.v_asistencia_diaria v
    JOIN {SCHEMA}.estudiantes e ON e.id_estudiante = v.id_estudiante
    WHERE v.fecha = :fecha
    ORDER BY e.apellidos, e.nombres, v.id_estudiante
    """
)


def _conteos() -> dict:
    """Expresiones de conteo por estado de asistencia."""
    return {
        "presentes": func.coalesce(
            func.sum(case((RegistroAsistencia.estado == "presente", 1), else_=0)), 0
        ),
        "tardanzas": func.coalesce(
            func.sum(case((RegistroAsistencia.estado == "tarde", 1), else_=0)), 0
        ),
        "ausencias": func.coalesce(
            func.sum(case((RegistroAsistencia.estado == "ausente", 1), else_=0)), 0
        ),
        "justificadas": func.coalesce(
            func.sum(case((RegistroAsistencia.estado == "justificada", 1), else_=0)), 0
        ),
        "pendientes": func.coalesce(
            func.sum(case((RegistroAsistencia.estado == "pendiente", 1), else_=0)), 0
        ),
    }


class ReportsRepository:
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

        El personal (dirección y profesorado) ve todos los reportes; el tutor
        solo ve los de los estudiantes a su cargo, con el vínculo confirmado por
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

    def cursos_de_profesor(self, id_usuario: int, id_gestion: int | None = None) -> list[int]:
        """Cursos en los que el profesor imparte en la gestión indicada."""
        stmt = (
            select(AsignacionDocente.id_curso)
            .join(Profesor, Profesor.id_profesor == AsignacionDocente.id_profesor)
            .where(Profesor.id_usuario == id_usuario)
        )
        if id_gestion is not None:
            stmt = stmt.where(AsignacionDocente.id_gestion == id_gestion)
        return list(db.session.execute(stmt).scalars().all())

    def get_curso(self, id_curso: int) -> Curso | None:
        return db.session.get(Curso, id_curso)

    def get_estudiante(self, id_estudiante: int) -> Estudiante | None:
        return db.session.get(Estudiante, id_estudiante)

    def estudiante_visible(self, id_estudiante: int, access) -> bool:
        stmt = select(Estudiante.id_estudiante).where(Estudiante.id_estudiante == id_estudiante)
        if access is not None:
            stmt = stmt.where(access)
        return db.session.execute(stmt).first() is not None

    def ids_visibles(self, access) -> list[tuple[int]]:
        """Identificadores de los estudiantes que el usuario puede ver."""
        stmt = select(Estudiante.id_estudiante).where(access)
        return list(db.session.execute(stmt).all())

    def cursos(self) -> list[Curso]:
        return list(db.session.execute(select(Curso).order_by(Curso.id_curso)).scalars().all())

    def cursos_por_estudiante(self, id_gestion: int) -> dict[int, dict]:
        """Curso de cada estudiante en la gestión indicada."""
        stmt = (
            select(
                Inscripcion.id_estudiante,
                Inscripcion.id_curso,
                Curso.nivel,
                Curso.grado,
                Curso.paralelo,
                Curso.turno,
            )
            .join(Curso, Curso.id_curso == Inscripcion.id_curso)
            .where(Inscripcion.id_gestion == id_gestion)
        )
        return {
            fila[0]: {
                "id_curso": fila[1],
                "nivel": fila[2],
                "grado": fila[3],
                "paralelo": fila[4],
                "turno": fila[5],
            }
            for fila in db.session.execute(stmt).all()
        }

    # ---------- resumen general ----------
    def resumen(self, id_gestion: int, id_curso: int | None = None, id_cursos=None) -> dict:
        """Totales de asistencia de la gestión activa."""
        conteos = _conteos()
        stmt = (
            select(
                func.count(RegistroAsistencia.id_asistencia).label("total_clases"),
                *[conteos[clave].label(clave) for clave in ("presentes", "tardanzas", "ausencias", "justificadas", "pendientes")],
            )
            .select_from(RegistroAsistencia)
            .join(SesionClase, SesionClase.id_sesion_clase == RegistroAsistencia.id_sesion_clase)
            .join(AsignacionDocente, AsignacionDocente.id_asignacion == SesionClase.id_asignacion)
            .where(AsignacionDocente.id_gestion == id_gestion)
        )
        stmt = self._filtro_curso(stmt, id_curso, id_cursos)
        fila = db.session.execute(stmt).one()

        sesiones = (
            select(func.count(func.distinct(SesionClase.id_sesion_clase)))
            .select_from(SesionClase)
            .join(AsignacionDocente, AsignacionDocente.id_asignacion == SesionClase.id_asignacion)
            .where(AsignacionDocente.id_gestion == id_gestion)
        )
        sesiones = self._filtro_curso(sesiones, id_curso, id_cursos)

        estudiantes = (
            select(func.count(func.distinct(Inscripcion.id_estudiante)))
            .select_from(Inscripcion)
            .where(Inscripcion.id_gestion == id_gestion, Inscripcion.estado == "inscrito")
        )
        if id_curso is not None:
            estudiantes = estudiantes.where(Inscripcion.id_curso == id_curso)

        datos = {
            "total_clases": int(fila.total_clases or 0),
            "presentes": int(fila.presentes or 0),
            "tardanzas": int(fila.tardanzas or 0),
            "ausencias": int(fila.ausencias or 0),
            "justificadas": int(fila.justificadas or 0),
            "pendientes": int(fila.pendientes or 0),
            "total_sesiones": int(db.session.execute(sesiones).scalar_one() or 0),
            "total_estudiantes": int(db.session.execute(estudiantes).scalar_one() or 0),
        }
        return datos

    @staticmethod
    def _filtro_curso(stmt, id_curso: int | None, id_cursos):
        if id_curso is not None:
            return stmt.where(AsignacionDocente.id_curso == id_curso)
        if id_cursos is not None:
            return stmt.where(AsignacionDocente.id_curso.in_(id_cursos))
        return stmt

    def resumen_por_curso(self, id_gestion: int, id_cursos=None) -> list[dict]:
        """Totales de asistencia agrupados por curso."""
        conteos = _conteos()
        stmt = (
            select(
                AsignacionDocente.id_curso,
                func.count(func.distinct(SesionClase.id_sesion_clase)).label("total_sesiones"),
                func.count(RegistroAsistencia.id_asistencia).label("total_clases"),
                *[conteos[clave].label(clave) for clave in ("presentes", "tardanzas", "ausencias", "justificadas", "pendientes")],
            )
            .select_from(AsignacionDocente)
            .join(SesionClase, SesionClase.id_asignacion == AsignacionDocente.id_asignacion)
            .outerjoin(
                RegistroAsistencia,
                RegistroAsistencia.id_sesion_clase == SesionClase.id_sesion_clase,
            )
            .where(AsignacionDocente.id_gestion == id_gestion)
            .group_by(AsignacionDocente.id_curso)
            .order_by(AsignacionDocente.id_curso)
        )
        if id_cursos is not None:
            stmt = stmt.where(AsignacionDocente.id_curso.in_(id_cursos))
        return [
            {
                "id_curso": fila.id_curso,
                "total_sesiones": int(fila.total_sesiones or 0),
                "total_clases": int(fila.total_clases or 0),
                "presentes": int(fila.presentes or 0),
                "tardanzas": int(fila.tardanzas or 0),
                "ausencias": int(fila.ausencias or 0),
                "justificadas": int(fila.justificadas or 0),
                "pendientes": int(fila.pendientes or 0),
            }
            for fila in db.session.execute(stmt).all()
        ]

    # ---------- asistencia por estudiante ----------
    def asistencia_por_estudiante(
        self,
        id_gestion: int,
        desde: date | None = None,
        hasta: date | None = None,
        id_curso: int | None = None,
        id_estudiante: int | None = None,
        access=None,
    ) -> list[dict]:
        """Una fila por estudiante con sus conteos de asistencia."""
        conteos = _conteos()
        stmt = (
            select(
                Estudiante.id_estudiante,
                Estudiante.codigo_estudiante,
                Estudiante.nombres,
                Estudiante.apellidos,
                func.count(RegistroAsistencia.id_asistencia).label("total_clases"),
                *[conteos[clave].label(clave) for clave in ("presentes", "tardanzas", "ausencias", "justificadas", "pendientes")],
            )
            .select_from(RegistroAsistencia)
            .join(SesionClase, SesionClase.id_sesion_clase == RegistroAsistencia.id_sesion_clase)
            .join(AsignacionDocente, AsignacionDocente.id_asignacion == SesionClase.id_asignacion)
            .join(Estudiante, Estudiante.id_estudiante == RegistroAsistencia.id_estudiante)
            .where(AsignacionDocente.id_gestion == id_gestion)
        )
        if desde is not None:
            stmt = stmt.where(SesionClase.fecha >= desde)
        if hasta is not None:
            stmt = stmt.where(SesionClase.fecha <= hasta)
        if id_curso is not None:
            stmt = stmt.where(AsignacionDocente.id_curso == id_curso)
        if id_estudiante is not None:
            stmt = stmt.where(RegistroAsistencia.id_estudiante == id_estudiante)
        if access is not None:
            stmt = stmt.where(access)
        stmt = stmt.group_by(
            Estudiante.id_estudiante,
            Estudiante.codigo_estudiante,
            Estudiante.nombres,
            Estudiante.apellidos,
        ).order_by(Estudiante.apellidos, Estudiante.nombres)
        return [
            {
                "id_estudiante": fila.id_estudiante,
                "codigo_estudiante": fila.codigo_estudiante,
                "nombres": fila.nombres,
                "apellidos": fila.apellidos,
                "total_clases": int(fila.total_clases or 0),
                "presentes": int(fila.presentes or 0),
                "tardanzas": int(fila.tardanzas or 0),
                "ausencias": int(fila.ausencias or 0),
                "justificadas": int(fila.justificadas or 0),
                "pendientes": int(fila.pendientes or 0),
            }
            for fila in db.session.execute(stmt).all()
        ]

    # ---------- detalle de un estudiante ----------
    def conteos_por_curso(self, id_estudiante: int, id_gestion: int) -> list[dict]:
        conteos = _conteos()
        stmt = (
            select(
                AsignacionDocente.id_curso,
                func.count(RegistroAsistencia.id_asistencia).label("total_clases"),
                *[conteos[clave].label(clave) for clave in ("presentes", "tardanzas", "ausencias", "justificadas", "pendientes")],
            )
            .select_from(RegistroAsistencia)
            .join(SesionClase, SesionClase.id_sesion_clase == RegistroAsistencia.id_sesion_clase)
            .join(AsignacionDocente, AsignacionDocente.id_asignacion == SesionClase.id_asignacion)
            .where(
                RegistroAsistencia.id_estudiante == id_estudiante,
                AsignacionDocente.id_gestion == id_gestion,
            )
            .group_by(AsignacionDocente.id_curso)
            .order_by(AsignacionDocente.id_curso)
        )
        return [
            {
                "id_curso": fila.id_curso,
                "total_clases": int(fila.total_clases or 0),
                "presentes": int(fila.presentes or 0),
                "tardanzas": int(fila.tardanzas or 0),
                "ausencias": int(fila.ausencias or 0),
                "justificadas": int(fila.justificadas or 0),
                "pendientes": int(fila.pendientes or 0),
            }
            for fila in db.session.execute(stmt).all()
        ]

    def conteos_por_mes(self, id_estudiante: int, id_gestion: int) -> list[dict]:
        conteos = _conteos()
        mes = func.date_trunc("month", SesionClase.fecha).label("mes")
        stmt = (
            select(
                mes,
                func.count(RegistroAsistencia.id_asistencia).label("total_clases"),
                *[conteos[clave].label(clave) for clave in ("presentes", "tardanzas", "ausencias", "justificadas", "pendientes")],
            )
            .select_from(RegistroAsistencia)
            .join(SesionClase, SesionClase.id_sesion_clase == RegistroAsistencia.id_sesion_clase)
            .join(AsignacionDocente, AsignacionDocente.id_asignacion == SesionClase.id_asignacion)
            .where(
                RegistroAsistencia.id_estudiante == id_estudiante,
                AsignacionDocente.id_gestion == id_gestion,
            )
            .group_by(mes)
            .order_by(mes)
        )
        return [
            {
                "mes": fila.mes.strftime("%Y-%m"),
                "total_clases": int(fila.total_clases or 0),
                "presentes": int(fila.presentes or 0),
                "tardanzas": int(fila.tardanzas or 0),
                "ausencias": int(fila.ausencias or 0),
                "justificadas": int(fila.justificadas or 0),
                "pendientes": int(fila.pendientes or 0),
            }
            for fila in db.session.execute(stmt).all()
        ]

    def ultimas_lecturas(self, id_estudiante: int, limite: int = 10) -> list[dict]:
        """Últimos registros de asistencia del estudiante."""
        stmt = (
            select(
                RegistroAsistencia,
                SesionClase,
                AsignacionDocente.id_curso,
            )
            .join(SesionClase, SesionClase.id_sesion_clase == RegistroAsistencia.id_sesion_clase)
            .join(AsignacionDocente, AsignacionDocente.id_asignacion == SesionClase.id_asignacion)
            .where(
                RegistroAsistencia.id_estudiante == id_estudiante,
                RegistroAsistencia.estado != "pendiente",
            )
            .order_by(SesionClase.fecha.desc(), SesionClase.hora_inicio_prevista.desc())
            .limit(limite)
        )
        return [
            {
                "id_asistencia": asistencia.id_asistencia,
                "id_sesion_clase": sesion.id_sesion_clase,
                "id_curso": id_curso,
                "fecha": sesion.fecha,
                "hora_inicio_prevista": sesion.hora_inicio_prevista,
                "estado": asistencia.estado,
                "hora_ingreso": asistencia.hora_ingreso,
                "metodo_ingreso": asistencia.metodo_ingreso,
            }
            for asistencia, sesion, id_curso in db.session.execute(stmt).all()
        ]

    # ---------- reporte diario ----------
    def diario(self, fecha: date) -> list[dict]:
        """Resumen del día tomado de la vista v_asistencia_diaria."""
        filas = db.session.execute(VISTA_DIARIA, {"fecha": fecha}).mappings().all()
        return [dict(fila) for fila in filas]
