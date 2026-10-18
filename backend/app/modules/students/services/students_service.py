"""Reglas de negocio de estudiantes (RF-02). No usa Flask ni escribe SQL."""
from dataclasses import dataclass

from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.core.errors.exceptions import DuplicateRecord, InvalidData, NotFound
from app.core.security.rbac import Principal
from app.modules.students.models.students import Curso, Estudiante, Inscripcion, ObservacionEstudiante
from app.modules.students.repositories.students_repository import StudentsRepository
from app.modules.students.services.guardian_link_service import GuardianLinkService

PERSONAL = ("director", "profesor")


@dataclass(frozen=True)
class StudentView:
    estudiante: Estudiante
    inscripcion: Inscripcion | None
    curso: Curso | None


def _es_personal(principal: Principal) -> bool:
    return bool(set(principal.roles) & set(PERSONAL))


class StudentsService:
    def __init__(self, repo=None, guardians=None):
        self.repo = repo or StudentsRepository()
        self.guardians = guardians or GuardianLinkService()

    # ---------- lectura ----------
    def _visible(self, principal: Principal, id_estudiante: int):
        gestion = self.repo.active_gestion()
        id_gestion = gestion.id_gestion if gestion else None
        access = self.repo.access_condition(principal.roles, principal.id_usuario, id_gestion)
        row = self.repo.get_visible(id_estudiante, id_gestion, access)
        if row is None:  # no se revela si existe o no (RD-02.1)
            raise NotFound("No se encontró el estudiante.", "Verifique el estudiante o regrese a la lista.")
        return row

    def list(self, principal: Principal, q, id_curso, estado, page, per_page):
        gestion = self.repo.active_gestion()
        id_gestion = gestion.id_gestion if gestion else None
        access = self.repo.access_condition(principal.roles, principal.id_usuario, id_gestion)
        rows, total = self.repo.search(id_gestion, access, q, id_curso, estado, page, per_page)
        return [StudentView(*r) for r in rows], total

    def get(self, principal: Principal, id_estudiante: int):
        est, insc, curso = self._visible(principal, id_estudiante)
        tutores = self.guardians.list_for_student(id_estudiante) if _es_personal(principal) else []
        return StudentView(est, insc, curso), tutores

    # ---------- escritura (director) ----------
    def create(self, principal: Principal, data) -> StudentView:
        gestion = self.repo.active_gestion()
        if gestion is None:
            raise InvalidData("No hay una gestión escolar activa.", "Active una gestión antes de registrar estudiantes.")
        curso = self.repo.get_curso(data.id_curso)
        if curso is None:
            raise NotFound("El curso indicado no existe.", "Elija un curso de la lista.")
        hoy = clock.now().date()
        if data.fecha_nacimiento >= hoy:
            raise InvalidData("La fecha de nacimiento no puede ser de hoy ni futura.", "Corrija la fecha e intente nuevamente.")
        if self.repo.code_exists(data.codigo_estudiante):
            raise DuplicateRecord(
                f"Ya existe un estudiante con el código '{data.codigo_estudiante}'.",
                "Use otro código o busque al estudiante en la lista.",
            )
        with unit_of_work():
            est = self.repo.add_student(
                Estudiante(
                    codigo_estudiante=data.codigo_estudiante,
                    nombres=data.nombres,
                    apellidos=data.apellidos,
                    fecha_nacimiento=data.fecha_nacimiento,
                    genero=data.genero,
                    estado="activo",
                )
            )
            insc = self.repo.add_enrollment(
                Inscripcion(
                    id_estudiante=est.id_estudiante,
                    id_curso=curso.id_curso,
                    id_gestion=gestion.id_gestion,
                    fecha_inscripcion=hoy,
                    estado="inscrito",
                )
            )
        return StudentView(est, insc, curso)

    def update(self, principal: Principal, id_estudiante: int, data) -> StudentView:
        est, insc, curso = self._visible(principal, id_estudiante)
        if est.estado != "activo":
            raise InvalidData("No se puede modificar a un estudiante retirado.", "Consulte la lista de estudiantes activos.")
        cambios = data.model_dump(exclude_unset=True)
        nuevo_curso_id = cambios.pop("id_curso", None)
        if "fecha_nacimiento" in cambios and cambios["fecha_nacimiento"] >= clock.now().date():
            raise InvalidData("La fecha de nacimiento no puede ser de hoy ni futura.", "Corrija la fecha e intente nuevamente.")
        nuevo_curso = None
        if nuevo_curso_id is not None:
            nuevo_curso = self.repo.get_curso(nuevo_curso_id)
            if nuevo_curso is None:
                raise NotFound("El curso indicado no existe.", "Elija un curso de la lista.")
        gestion = self.repo.active_gestion()
        with unit_of_work():
            for campo, valor in cambios.items():
                setattr(est, campo, valor)
            if nuevo_curso is not None:
                if insc is None:
                    insc = self.repo.add_enrollment(
                        Inscripcion(
                            id_estudiante=id_estudiante,
                            id_curso=nuevo_curso.id_curso,
                            id_gestion=gestion.id_gestion,
                            fecha_inscripcion=clock.now().date(),
                            estado="inscrito",
                        )
                    )
                else:
                    insc.id_curso = nuevo_curso.id_curso
                curso = nuevo_curso
        return StudentView(est, insc, curso)

    def withdraw(self, principal: Principal, id_estudiante: int) -> None:
        """Dar de baja: el estudiante pasa a 'retirado'. No se borra, para conservar su historial (RNF-06.1)."""
        est, insc, _ = self._visible(principal, id_estudiante)
        if est.estado == "retirado":
            raise InvalidData("El estudiante ya está retirado.", "No hace falta repetir la baja.")
        with unit_of_work():
            est.estado = "retirado"
            if insc is not None and insc.estado == "inscrito":
                insc.estado = "retirado"

    # ---------- observaciones (RF-02.2) ----------
    def add_observation(self, principal: Principal, id_estudiante: int, tipo, descripcion, confidencial) -> ObservacionEstudiante:
        self._visible(principal, id_estudiante)
        with unit_of_work():
            return self.repo.add_observation(
                ObservacionEstudiante(
                    id_estudiante=id_estudiante,
                    registrada_por=principal.id_usuario,
                    fecha_hora=clock.now(),
                    tipo=tipo,
                    descripcion=descripcion,
                    confidencial=confidencial,
                    estado="activa",
                )
            )

    def list_observations(self, principal: Principal, id_estudiante: int):
        self._visible(principal, id_estudiante)
        return self.repo.list_observations(id_estudiante, principal.id_usuario, ve_todo="director" in principal.roles)

    # ---------- tutores (RD-02.2) ----------
    def link_guardian(self, principal: Principal, id_estudiante: int, id_tutor: int, parentesco: str, es_principal: bool):
        self._visible(principal, id_estudiante)
        self.guardians.link(id_estudiante, id_tutor, parentesco, es_principal)

    def confirm_guardian(self, principal: Principal, id_estudiante: int, id_tutor: int):
        self._visible(principal, id_estudiante)
        self.guardians.confirm(id_estudiante, id_tutor, principal.id_usuario)