import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# backend/.env
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DEFAULT_SECRET = "cambia_esto"


class BaseConfig:
    ENV_NAME = "base"
    SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", DEFAULT_SECRET)
    # Clave con la que se cifran los secretos TOTP de cada estudiante.
    TOTP_ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", DEFAULT_SECRET)
    # Límite absoluto del token; la inactividad (15 min) se controla en la base de datos.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        # RD-01.3: todas las conexiones trabajan con la hora oficial de Bolivia (UTC-4)
        "connect_args": {"options": "-c timezone=America/La_Paz"},
    }

    MAX_CONTENT_LENGTH = 100 * 1024  # RNF-01.3: máximo 100 KB por transacción
    SESSION_IDLE_MINUTES = 15  # RNF-02.3: cierre por inactividad
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # Planificador de tareas (APScheduler): apagado por defecto en desarrollo.
    SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "si",
    }
    # Antigüedad máxima (en días) de los eventos de la bitácora de auditoría.
    AUDIT_PURGE_DAYS = int(os.getenv("AUDIT_PURGE_DAYS", "365"))

    # Tareas programadas (detección de alertas, purga de auditoría).
    SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "false").lower() == "true"
    SCHEDULER_INTERVAL_HORAS = int(os.getenv("SCHEDULER_INTERVAL_HORAS", "24"))
    AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "365"))

    # Registro de la aplicación.
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
