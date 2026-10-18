from flask import Blueprint, current_app, request
from flask_jwt_extended import verify_jwt_in_request

from app.core.security.tokens import create_token, session_id_from_token
from app.modules.auth.api.guards import auth_required, current_principal, get_auth_service
from app.modules.auth.api.schemas import LoginRequest, parse_json, user_payload

bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    data = parse_json(LoginRequest)
    result = get_auth_service().login(data.nombre_usuario, data.contrasena, request.remote_addr)
    return {
        "access_token": create_token(result.usuario.id_usuario, result.sesion.id_sesion),
        "inactividad_max_minutos": current_app.config["SESSION_IDLE_MINUTES"],
        "usuario": user_payload(result.usuario, result.usuario.nombres_roles),
    }


@bp.post("/logout")
def logout():
    verify_jwt_in_request()
    get_auth_service().logout(session_id_from_token())
    return {"mensaje": "Sesión cerrada correctamente."}


@bp.get("/me")
@auth_required()
def me():
    p = current_principal()
    return {
        "id_usuario": p.id_usuario,
        "nombres": p.nombres,
        "apellidos": p.apellidos,
        "nombre_usuario": p.nombre_usuario,
        "roles": list(p.roles),
    }