"""Consulta pública para otros módulos: nombres de usuarios por id."""
from app.modules.auth.repositories.auth_repository import UsuarioRepository


def display_names(user_ids) -> dict[int, str]:
    ids = set(user_ids)
    return UsuarioRepository().names_by_ids(ids) if ids else {}