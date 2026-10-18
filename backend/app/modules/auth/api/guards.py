from functools import wraps

from flask import current_app, g
from flask_jwt_extended import verify_jwt_in_request

from app.core.errors.exceptions import PermissionDenied
from app.core.security.rbac import Principal, has_any_role
from app.core.security.tokens import session_id_from_token
from app.modules.auth.services.auth_service import AuthService


def get_auth_service() -> AuthService:
    return AuthService(idle_minutes=current_app.config["SESSION_IDLE_MINUTES"])


def auth_required(*roles: str):
    """Exige sesión activa y, si se indican, alguno de los roles. Uso: @auth_required("director")."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            principal = get_auth_service().authenticate_session(session_id_from_token())
            if not has_any_role(principal.roles, roles):
                raise PermissionDenied()
            g.principal = principal
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def current_principal() -> Principal:
    return g.principal