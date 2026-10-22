from .messages import MESSAGES


class AppError(Exception):
    """Error de aplicación con mensaje claro: causa y acción a seguir."""

    code = "error_interno"
    status_code = 500

    def __init__(self, message: str | None = None, action: str | None = None):
        default_message, default_action = MESSAGES[self.code]
        self.message = message or default_message
        self.action = action or default_action
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {"error": {"codigo": self.code, "mensaje": self.message, "accion": self.action}}


class InvalidCredentials(AppError):
    code = "credenciales_invalidas"
    status_code = 401


class NotAuthenticated(AppError):
    code = "no_autenticado"
    status_code = 401


class InvalidToken(AppError):
    code = "token_invalido"
    status_code = 401


class SessionExpired(AppError):
    code = "sesion_expirada"
    status_code = 401


class SessionClosed(AppError):
    code = "sesion_cerrada"
    status_code = 401


class AccountInactive(AppError):
    code = "cuenta_inactiva"
    status_code = 403


class NoRoleAssigned(AppError):
    code = "sin_rol"
    status_code = 403


class PermissionDenied(AppError):
    code = "sin_permiso"
    status_code = 403


class InvalidData(AppError):
    code = "datos_invalidos"
    status_code = 422


class NotFound(AppError):
    code = "no_encontrado"
    status_code = 404


class DuplicateRecord(AppError):
    code = "registro_duplicado"
    status_code = 409
