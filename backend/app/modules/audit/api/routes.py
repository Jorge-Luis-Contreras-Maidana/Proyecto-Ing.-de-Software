"""Rutas HTTP de la bitácora de auditoría. Solo la dirección tiene acceso."""
from flask import Blueprint

from app.core.http import parse_query
from app.modules.audit.api.schemas import AuditListQuery, evento_payload
from app.modules.audit.services.audit_service import AuditService
from app.modules.auth import auth_required, current_principal

bp = Blueprint("audit", __name__)


def _service() -> AuditService:
    return AuditService()


@bp.get("")
@auth_required("director")
def listar_eventos():
    f = parse_query(AuditListQuery)
    eventos, total = _service().listar(
        current_principal(),
        f.operacion,
        f.entidad,
        f.id_usuario,
        f.desde,
        f.hasta,
        f.page,
        f.per_page,
    )
    return {
        "items": [evento_payload(e) for e in eventos],
        "total": total,
        "page": f.page,
        "per_page": f.per_page,
    }


@bp.get("/<int:id_evento>")
@auth_required("director")
def obtener_evento(id_evento: int):
    return evento_payload(_service().obtener(current_principal(), id_evento))
