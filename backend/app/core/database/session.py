from app.extensions import db


def get_session():
    """Sesión de base de datos de la petición actual."""
    return db.session
