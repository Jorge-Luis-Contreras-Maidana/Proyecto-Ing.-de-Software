from pydantic import BaseModel, Field

from app.core.http import parse_json  # noqa: F401  (se reexporta para las rutas)


class LoginRequest(BaseModel):
    nombre_usuario: str = Field(min_length=1, max_length=60)
    contrasena: str = Field(min_length=1, max_length=200)


def user_payload(usuario, roles) -> dict:
    return {
        "id_usuario": usuario.id_usuario,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "nombre_usuario": usuario.nombre_usuario,
        "roles": list(roles),
        "debe_cambiar_contrasena": usuario.debe_cambiar_contrasena,
    }