"""Lectura y validación de los datos que llegan en las peticiones."""
from flask import request
from pydantic import BaseModel, ValidationError

from app.core.errors.exceptions import InvalidData


def _invalid(err: ValidationError) -> InvalidData:
    campo = ".".join(str(p) for p in err.errors()[0]["loc"]) or "datos"
    return InvalidData(f"El campo '{campo}' es obligatorio o no es válido.", "Corríjalo e intente nuevamente.")


def parse_json(model: type[BaseModel]):
    """Cuerpo JSON de la petición."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise InvalidData("No se recibieron datos válidos.", "Envíe la información en formato JSON.")
    try:
        return model.model_validate(payload)
    except ValidationError as err:
        raise _invalid(err)


def parse_query(model: type[BaseModel]):
    """Parámetros de la dirección (?pagina=2&q=...)."""
    try:
        return model.model_validate(request.args.to_dict())
    except ValidationError as err:
        raise _invalid(err)