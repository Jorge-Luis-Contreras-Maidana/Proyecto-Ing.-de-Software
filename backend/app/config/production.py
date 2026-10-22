import os

from .base import BaseConfig


class ProductionConfig(BaseConfig):
    ENV_NAME = "production"
    DEBUG = False
    # En producción el planificador de tareas está encendido por defecto.
    SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "si",
    }
