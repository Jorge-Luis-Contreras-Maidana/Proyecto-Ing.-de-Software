"""Rutas del módulo de seguimiento de asistencia."""
from flask import Blueprint

from app.core.http import parse_json, parse_query
from app.modules.auth import auth_required, current_principal
from app.modules.followup.api.schemas import (
    AlertaCreate,
    AlertaEstadoUpdate,
    AlertaListQuery,
    alerta_payload,
)
from app.modules.followup.services.followup_service import FollowupService

bp = Blueprint("followup", __name__)


def _service() -> FollowupService:
    return FollowupService()


@bp.get("/alertas")
@auth_required("director", "profesor", "tutor")
def list_alertas():
    """Alertas de seguimiento. El tutor solo ve las de los estudiantes a su cargo."""
    f = parse_query(AlertaListQuery)
    alertas, total = _service().listar(current_principal(), f.estado, f.id_estudiante, f.id_curso)
    return {"items": [alerta_payload(a) for a in alertas], "total": total}


@bp.get("/alertas/<int:id_alerta>")
@auth_required("director", "profesor", "tutor")
def get_alerta(id_alerta: int):
    """Detalle de una alerta de seguimiento."""
    return alerta_payload(_service().obtener(current_principal(), id_alerta))


@bp.post("/alertas")
@auth_required("director", "profesor")
def create_alerta():
    """Registra una alerta de seguimiento."""
    data = parse_json(AlertaCreate)
    alerta = _service().crear(
        current_principal(),
        data.id_estudiante,
        data.id_curso,
        data.tipo,
        data.descripcion,
        data.asignada_a,
    )
    return alerta_payload(alerta), 201


@bp.put("/alertas/<int:id_alerta>/estado")
@auth_required("director", "profesor")
def update_alerta_estado(id_alerta: int):
    """Cambia el estado de una alerta de seguimiento."""
    data = parse_json(AlertaEstadoUpdate)
    alerta = _service().cambiar_estado(current_principal(), id_alerta, data.estado, data.observacion)
    return alerta_payload(alerta)


@bp.post("/detectar")
@auth_required("director")
def detectar_alertas():
    """Detecta patrones de inasistencia y genera las alertas que falten."""
    creadas, omitidas = _service().detectar(current_principal())
    return {
        "items": [alerta_payload(a) for a in creadas],
        "creadas": len(creadas),
        "omitidas": omitidas,
    }


@bp.get("/estudiante/<int:id_estudiante>")
@auth_required("director", "profesor", "tutor")
def alertas_de_estudiante(id_estudiante: int):
    """Alertas de seguimiento de un estudiante."""
    alertas = _service().alertas_de_estudiante(current_principal(), id_estudiante)
    return {"items": [alerta_payload(a) for a in alertas], "total": len(alertas)}
