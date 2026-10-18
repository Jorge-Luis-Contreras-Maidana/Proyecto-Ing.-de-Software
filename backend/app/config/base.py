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