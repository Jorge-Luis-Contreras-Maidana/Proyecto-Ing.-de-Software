from flask_jwt_extended import create_access_token, get_jwt

from app.core.errors.exceptions import InvalidToken


def create_token(user_id: int, session_id: int) -> str:
    return create_access_token(identity=str(user_id), additional_claims={"sid": session_id})


def session_id_from_token() -> int:
    """Lee el id de sesión del token ya verificado."""
    try:
        return int(get_jwt()["sid"])
    except (KeyError, TypeError, ValueError) as err:
        raise InvalidToken() from err
