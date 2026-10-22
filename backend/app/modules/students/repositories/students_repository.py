from sqlalchemy import and_, false, func, or_, select
from sqlalchemy.exc import IntegrityError

from app.core.errors.exceptions import DuplicateRecord
from app.core.text.search import coincide
from app.extensions import db
from app.modules.students.models.guardian_link import EstudianteTutor, Tutor
from app.modules.students.models.students import (
    AsignacionDocente,
    Curso,
    Estudiante,
    GestionEscolar,
    Inscripcion,
    ObservacionEstudiante,
    Profesor,
)


class StudentsRepository:
    # ---------- gestión y cursos ----------
    def active_gestion(self) -> GestionEscolar | None:
        stmt = select(GestionEscolar).where(GestionEscolar.estado == "activa").order_by(GestionEscolar.anio.desc()).limit(1)
        return db.session.execute(stmt).scalar_one_or_none()

    def get_curso(self, id_curso: int) -> Curso | None:
        return db.session.get(Curso, id_curso)

    # ---------- acceso por fila (RD-02.1) ----------
    def access_condition(self, roles, user_id: int, id_gestion: int | None):
        """Condición SQL con los estudiantes que el usuario puede ver. None = sin restricción."""
        if "director" in roles:
            return None
        conds = []
        if "profesor" in roles and id_gestion is not None:
            cursos = (
                select(AsignacionDocente.id_curso)
                .join(Profesor, Profesor.id_profesor == AsignacionDocente.id_profesor)
                .where(Profesor.id_usuario == user_id, AsignacionDocente.id_gestion == id_gestion)
            )
            de_mis_cursos = select(Inscripcion.id_estudiante).where(
                Inscripcion.id_gestion == id_gestion, Inscripcion.id_curso.in_(cursos)
            )
            conds.append(Estudiante.id_estudiante.in_(de_mis_cursos))
        if "tutor" in roles:
            hijos = (
                select(EstudianteTutor.id_estudiante)
                .join(Tutor, Tutor.id_tutor == EstudianteTutor.id_tutor)
                .where(Tutor.id_usuario == user_id, EstudianteTutor.confirmado.is_(True))
            )
            conds.append(Estudiante.id_estudiante.in_(hijos))
        if "estudiante" in roles:
            conds.append(Estudiante.id_usuario == user_id)
        return or_(*conds) if conds else false()

    # ---------- consultas ----------
    def _joined(self, stmt, id_gestion):
        gestion = id_gestion if id_gestion is not None else -1
        return (
            stmt.select_from(Estudiante)
            .outerjoin(Inscripcion, and_(Inscripcion.id_estudiante == Estudiante.id_estudiante, Inscripcion.id_gestion == gestion))
            .outerjoin(Curso, Curso.id_curso == Inscripcion.id_curso)
        )

    def search(self, id_gestion, access, q, id_curso, estado, page, per_page):
        conds = []
        if access is not None:
            conds.append(access)
        if estado:
            conds.append(Estudiante.estado == estado)
        if id_curso:
            conds.append(Inscripcion.id_curso == id_curso)
        if q:
            conds.append(
                or_(
                    coincide(Estudiante.nombres + " " + Estudiante.apellidos, q),
                    coincide(Estudiante.codigo_estudiante, q),
                )
            )
        total = db.session.scalar(self._joined(select(func.count(Estudiante.id_estudiante)), id_gestion).where(*conds))
        stmt = (
            self._joined(select(Estudiante, Inscripcion, Curso), id_gestion)
            .where(*conds)
            .order_by(Estudiante.apellidos, Estudiante.nombres, Estudiante.id_estudiante)
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        return db.session.execute(stmt).all(), total

    def get_visible(self, id_estudiante: int, id_gestion, access):
        conds = [Estudiante.id_estudiante == id_estudiante]
        if access is not None:
            conds.append(access)
        stmt = self._joined(select(Estudiante, Inscripcion, Curso), id_gestion).where(*conds)
        return db.session.execute(stmt).first()

    def code_exists(self, codigo: str) -> bool:
        stmt = select(func.count(Estudiante.id_estudiante)).where(func.lower(Estudiante.codigo_estudiante) == codigo.lower())
        return db.session.scalar(stmt) > 0

    # ---------- escritura ----------
    def add_student(self, estudiante: Estudiante) -> Estudiante:
        try:
            db.session.add(estudiante)
            db.session.flush()
        except IntegrityError as err:
            db.session.rollback()
            raise DuplicateRecord(
                f"Ya existe un estudiante con el código '{estudiante.codigo_estudiante}'.",
                "Use otro código o busque al estudiante en la lista.",
            ) from err
        return estudiante

    def add_enrollment(self, inscripcion: Inscripcion) -> Inscripcion:
        db.session.add(inscripcion)
        db.session.flush()
        return inscripcion

    def get_enrollment(self, id_estudiante: int, id_gestion: int) -> Inscripcion | None:
        stmt = select(Inscripcion).where(Inscripcion.id_estudiante == id_estudiante, Inscripcion.id_gestion == id_gestion)
        return db.session.execute(stmt).scalar_one_or_none()

    # ---------- observaciones (RF-02.2) ----------
    def add_observation(self, obs: ObservacionEstudiante) -> ObservacionEstudiante:
        db.session.add(obs)
        db.session.flush()
        return obs

    def list_observations(self, id_estudiante: int, user_id: int, ve_todo: bool):
        stmt = select(ObservacionEstudiante).where(
            ObservacionEstudiante.id_estudiante == id_estudiante, ObservacionEstudiante.estado == "activa"
        )
        if not ve_todo:  # las confidenciales solo las ve el director o quien las escribió
            stmt = stmt.where(
                or_(ObservacionEstudiante.confidencial.is_(False), ObservacionEstudiante.registrada_por == user_id)
            )
        return db.session.execute(stmt.order_by(ObservacionEstudiante.fecha_hora.desc())).scalars().all()


class GuardianLinkRepository:
    def get_tutor(self, id_tutor: int) -> Tutor | None:
        return db.session.get(Tutor, id_tutor)

    def get_link(self, id_estudiante: int, id_tutor: int) -> EstudianteTutor | None:
        return db.session.get(EstudianteTutor, (id_estudiante, id_tutor))

    def principal_link(self, id_estudiante: int) -> EstudianteTutor | None:
        stmt = select(EstudianteTutor).where(
            EstudianteTutor.id_estudiante == id_estudiante, EstudianteTutor.es_contacto_principal.is_(True)
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def add_link(self, link: EstudianteTutor) -> EstudianteTutor:
        db.session.add(link)
        db.session.flush()
        return link

    def list_for_student(self, id_estudiante: int):
        stmt = (
            select(EstudianteTutor, Tutor)
            .join(Tutor, Tutor.id_tutor == EstudianteTutor.id_tutor)
            .where(EstudianteTutor.id_estudiante == id_estudiante)
            .order_by(EstudianteTutor.es_contacto_principal.desc(), EstudianteTutor.id_tutor)
        )
        return db.session.execute(stmt).all()
