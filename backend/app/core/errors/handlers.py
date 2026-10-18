import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from app.extensions import db
from .exceptions import AppError, InvalidToken, NotAuthenticated, SessionExpired
from .messages import MESSAGES

log = logging.getLogger(__name__)

_HTTP_CODES = {404: "no_encontrado", 405: "metodo_no_permitido", 413: "solicitud_demasiado_grande"}


def _payload(code: str) -> dict:
    message, action = MESSAGES[code]
    return {"error": {"codigo": code, "mensaje": message, "accion": action}}


def register_error_handlers(app, jwt) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(err: AppError):
        db.session.rollback()
        return err.to_dict(), err.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(err: HTTPException):
        db.session.rollback()
        code = _HTTP_CODES.get(err.code)
        if code:
            return _payload(code), err.code
        return _payload("error_interno"), err.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected(err: Exception):
        db.session.rollback()
        log.exception("Error no controlado")
        return _payload("error_interno"), 500

    # Errores del token JWT en el mismo formato
    @jwt.unauthorized_loader
    def _no_token(_reason):
        db.session.rollback()
        return NotAuthenticated().to_dict(), 401

    @jwt.invalid_token_loader
    def _bad_token(_reason):
        db.session.rollback()
        return InvalidToken().to_dict(), 401

    @jwt.expired_token_loader
    def _expired_token(_header, _payload_):
        db.session.rollback()
        return SessionExpired().to_dict(), 401