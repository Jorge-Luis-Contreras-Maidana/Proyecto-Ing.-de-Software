from flask import Blueprint

from app.core.errors.exceptions import NotFound
from app.modules.auth import auth_required, current_principal
from app.modules.justifications.api.schemas import (
    JustificacionCreate,
    JustificacionEstado,
    JustificacionListQuery,
    justificacion_payload,
    parse_json,
    parse_query,
)
from app.modules.justifications.services.justifications_service import JustificationsService

bp = Blueprint("justifications", __name__)


def _service() -> JustificationsService:
    return JustificationsService()


@bp.get("")
@auth_required("director", "profesor", "tutor")
def listar_justificaciones():
    f = parse_query(JustificacionListQuery)
    items = _service().list(current_principal(), f.estado, f.id_estudiante)
    return {"items": [justificacion_payload(j) for j in items], "total": len(items)}


@bp.get("/<int:id_justificacion>")
@auth_required("director", "profesor", "tutor")
def obtener_justificacion(id_justificacion: int):
    items = _service().list(current_principal())
    for j in items:
        if j.id_justificacion == id_justificacion:
            return justificacion_payload(j)
    raise NotFound("No se encontró la justificación.", "Verifique la justificación o regrese al inicio.")


@bp.post("")
@auth_required("tutor")
def crear_justificacion():
    data = parse_json(JustificacionCreate)
    nueva = _service().crear(
        current_principal(),
        data.id_estudiante,
        data.fecha_inicio,
        data.fecha_fin,
        data.motivo,
        data.documento_referencia,
    )
    return justificacion_payload(nueva), 201


@bp.put("/<int:id_justificacion>/estado")
@auth_required("director")
def cambiar_estado_justificacion(id_justificacion: int):
    data = parse_json(JustificacionEstado)
    j = _service().revisar(current_principal(), id_justificacion, data.estado, data.comentario)
    return justificacion_payload(j)
