"""Rutas HTTP de los avisos institucionales."""
from flask import Blueprint

from app.core.http import parse_json, parse_query
from app.modules.announcements.api.schemas import (
    AvisoCreate,
    AvisoInasistenciaCreate,
    AvisoListQuery,
    AvisoUpdate,
    aviso_inasistencia_payload,
    aviso_payload,
)
from app.modules.announcements.services.announcements_service import AnnouncementsService
from app.modules.auth import auth_required, current_principal

bp = Blueprint("announcements", __name__)


def _service() -> AnnouncementsService:
    return AnnouncementsService()


@bp.get("")
@auth_required()
def listar_avisos():
    f = parse_query(AvisoListQuery)
    vistas, total = _service().listar(
        current_principal(), f.estado, f.solo_no_leidos, f.page, f.per_page
    )
    return {
        "items": [aviso_payload(v) for v in vistas],
        "total": total,
        "page": f.page,
        "per_page": f.per_page,
    }


@bp.get("/inasistencia-docente")
@auth_required("director", "profesor")
def listar_avisos_inasistencia_docente():
    avisos = _service().listar_inasistencia(current_principal())
    return {"items": [aviso_inasistencia_payload(a) for a in avisos]}


@bp.post("/inasistencia-docente")
@auth_required("director")
def crear_aviso_inasistencia_docente():
    d = parse_json(AvisoInasistenciaCreate)
    aviso = _service().crear_inasistencia(current_principal(), d)
    return aviso_inasistencia_payload(aviso), 201


@bp.get("/<int:id_aviso>")
@auth_required()
def obtener_aviso(id_aviso: int):
    return aviso_payload(_service().obtener(current_principal(), id_aviso))


@bp.post("")
@auth_required("director")
def crear_aviso():
    d = parse_json(AvisoCreate)
    return aviso_payload(_service().crear(current_principal(), d)), 201


@bp.put("/<int:id_aviso>")
@auth_required("director")
def actualizar_aviso(id_aviso: int):
    d = parse_json(AvisoUpdate)
    return aviso_payload(_service().actualizar(current_principal(), id_aviso, d))


@bp.post("/<int:id_aviso>/publicar")
@auth_required("director")
def publicar_aviso(id_aviso: int):
    return aviso_payload(_service().publicar(current_principal(), id_aviso))


@bp.put("/<int:id_aviso>/leer")
@auth_required()
def marcar_aviso_leido(id_aviso: int):
    return aviso_payload(_service().marcar_leido(current_principal(), id_aviso))
