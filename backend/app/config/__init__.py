import os

from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig

_CONFIGS = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(name: str | None = None):
    name = name or os.getenv("FLASK_ENV", "development")
    try:
        return _CONFIGS[name]
    except KeyError as err:
        raise RuntimeError(
            f"Configuración desconocida: '{name}'. Use development, production o testing."
        ) from err
