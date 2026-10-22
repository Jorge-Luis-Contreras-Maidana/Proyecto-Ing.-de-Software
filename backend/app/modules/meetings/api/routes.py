"""Rutas del módulo de citas de seguimiento."""
from flask import Blueprint

from app.core.http import parse_json, parse_query
from app.modules.auth import auth_required, current_principal
from app.modules.meetings.api.schemas import (
    CitacionCreate,
    CitacionEstadoUpdate,
    CitacionListQuery,
    citacion_payload,
)
from app.modules.meetings.services.meetings_service import MeetingsService

bp = Blueprint("meetings", __name__)


def _service() -> MeetingsService:
    return MeetingsService()


@bp.get("")
@auth_required("director", "profesor", "tutor")
def list_citas():
    """Citas de seguimiento. El tutor solo ve las de los estudiantes a su cargo."""
    f = parse_query(CitacionListQuery)
    citas, total = _service().listar(current_principal(), f.estado, f.id_estudiante)
    return {"items": [citacion_payload(c) for c in citas], "total": total}


@bp.get("/<int:id_citacion>")
@auth_required("director", "profesor", "tutor")
def get_citacion(id_citacion: int):
    """Detalle de una cita de seguimiento."""
    return citacion_payload(_service().obtener(current_principal(), id_citacion))


@bp.post("")
@auth_required("director", "profesor")
def create_citacion():
    """Programa una cita entre el profesor y el tutor."""
    data = parse_json(CitacionCreate)
    citacion = _service().crear(
        current_principal(),
        data.id_estudiante,
        data.id_tutor,
        data.id_profesor,
        data.id_alerta,
        data.fecha_hora,
        data.motivo,
        data.observaciones,
    )
    return citacion_payload(citacion), 201


@bp.put("/<int:id_citacion>/estado")
@auth_required("director", "profesor")
def update_citacion_estado(id_citacion: int):
    """Cambia el estado de una cita de seguimiento."""
    data = parse_json(CitacionEstadoUpdate)
    citacion = _service().cambiar_estado(
        current_principal(), id_citacion, data.estado, data.observaciones
    )
    return citacion_payload(citacion)
