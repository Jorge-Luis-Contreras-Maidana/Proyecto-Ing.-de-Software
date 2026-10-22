"""Rutas HTTP de las notificaciones. Cada usuario solo accede a las suyas."""
from flask import Blueprint

from app.core.http import parse_json, parse_query
from app.modules.auth import auth_required, current_principal
from app.modules.notifications.api.schemas import (
    NotificacionCreate,
    NotificacionListQuery,
    notificacion_payload,
)
from app.modules.notifications.services.notifications_service import NotificationsService

bp = Blueprint("notifications", __name__)


def _service() -> NotificationsService:
    return NotificationsService()


@bp.get("")
@auth_required()
def listar_notificaciones():
    f = parse_query(NotificacionListQuery)
    items, total, no_leidas = _service().listar(current_principal(), f.page, f.per_page)
    return {
        "items": [notificacion_payload(n) for n in items],
        "total": total,
        "no_leidas": no_leidas,
        "page": f.page,
        "per_page": f.per_page,
    }


@bp.get("/no-leidas")
@auth_required()
def contar_no_leidas():
    return {"no_leidas": _service().no_leidas(current_principal())}


@bp.put("/leer-todas")
@auth_required()
def leer_todas_las_notificaciones():
    actualizadas = _service().leer_todas(current_principal())
    return {"actualizadas": actualizadas}


@bp.put("/<int:id_notificacion>/leer")
@auth_required()
def marcar_notificacion_leida(id_notificacion: int):
    notificacion = _service().marcar_leida(current_principal(), id_notificacion)
    return notificacion_payload(notificacion)


@bp.post("")
@auth_required("director")
def crear_notificacion():
    d = parse_json(NotificacionCreate)
    notificacion = _service().crear(
        current_principal(),
        d.id_usuario_destinatario,
        d.tipo,
        d.titulo,
        d.mensaje,
        d.entidad_referencia,
        d.id_referencia,
    )
    return notificacion_payload(notificacion), 201
