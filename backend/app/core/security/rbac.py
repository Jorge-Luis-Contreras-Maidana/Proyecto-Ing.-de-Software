"""Control de acceso basado en roles. RF-01.3."""
from dataclasses import dataclass

ROL_DIRECTOR = "director"
ROL_PROFESOR = "profesor"
ROL_TUTOR = "tutor"
ROL_ESTUDIANTE = "estudiante"


@dataclass(frozen=True)
class Principal:
    """Usuario autenticado de la petición actual."""

    id_usuario: int
    id_sesion: int
    nombre_usuario: str
    nombres: str
    apellidos: str
    roles: tuple[str, ...]


def has_any_role(user_roles, allowed) -> bool:
    """True si no se exige rol, o si el usuario tiene al menos uno de los permitidos."""
    return not allowed or bool(set(user_roles) & set(allowed))
