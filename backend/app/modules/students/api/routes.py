from flask import Blueprint

from app.core.http import parse_json, parse_query
from app.modules.auth import auth_required, current_principal
from app.modules.students.api.schemas import (
    GuardianLinkCreate,
    ObservationCreate,
    StudentCreate,
    StudentListQuery,
    StudentUpdate,
    observation_payload,
    student_payload,
)
from app.modules.students.services.students_service import StudentsService

bp = Blueprint("students", __name__)


def _service() -> StudentsService:
    return StudentsService()


@bp.get("")
@auth_required()
def list_students():
    f = parse_query(StudentListQuery)
    estado = None if f.estado == "todos" else f.estado
    views, total = _service().list(current_principal(), f.q, f.id_curso, estado, f.page, f.per_page)
    return {
        "items": [student_payload(v) for v in views],
        "total": total,
        "page": f.page,
        "per_page": f.per_page,
    }


@bp.get("/<int:id_estudiante>")
@auth_required()
def get_student(id_estudiante: int):
    view, tutores = _service().get(current_principal(), id_estudiante)
    return student_payload(view, tutores)


@bp.post("")
@auth_required("director")
def create_student():
    data = parse_json(StudentCreate)
    view = _service().create(current_principal(), data)
    return student_payload(view), 201


@bp.put("/<int:id_estudiante>")
@auth_required("director")
def update_student(id_estudiante: int):
    data = parse_json(StudentUpdate)
    return student_payload(_service().update(current_principal(), id_estudiante, data))


@bp.delete("/<int:id_estudiante>")
@auth_required("director")
def withdraw_student(id_estudiante: int):
    _service().withdraw(current_principal(), id_estudiante)
    return {"mensaje": "El estudiante fue dado de baja."}


@bp.get("/<int:id_estudiante>/observaciones")
@auth_required("director", "profesor")
def list_observations(id_estudiante: int):
    obs = _service().list_observations(current_principal(), id_estudiante)
    return {"items": [observation_payload(o) for o in obs]}


@bp.post("/<int:id_estudiante>/observaciones")
@auth_required("director", "profesor")
def add_observation(id_estudiante: int):
    d = parse_json(ObservationCreate)
    obs = _service().add_observation(current_principal(), id_estudiante, d.tipo, d.descripcion, d.confidencial)
    return observation_payload(obs), 201


@bp.post("/<int:id_estudiante>/tutores")
@auth_required("director")
def link_guardian(id_estudiante: int):
    d = parse_json(GuardianLinkCreate)
    _service().link_guardian(current_principal(), id_estudiante, d.id_tutor, d.parentesco, d.es_contacto_principal)
    return {"mensaje": "Tutor vinculado. Falta la confirmación del director."}, 201


@bp.post("/<int:id_estudiante>/tutores/<int:id_tutor>/confirmar")
@auth_required("director")
def confirm_guardian(id_estudiante: int, id_tutor: int):
    _service().confirm_guardian(current_principal(), id_estudiante, id_tutor)
    return {"mensaje": "Vínculo confirmado."}
