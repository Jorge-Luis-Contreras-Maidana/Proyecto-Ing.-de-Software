"""Configuración de los registros de la aplicación.

Un solo formato para toda la app: fecha, nivel, módulo y mensaje. Los errores
inesperados se registran con su traza completa para poder reconstruirlos.
"""
import logging
import logging.handlers
import os
import sys

FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
FECHA = "%Y-%m-%d %H:%M:%S"

_configurado = False


def configure_logging(app=None, nivel: str | None = None) -> logging.Logger:
    """Configura el logger raíz de la aplicación. Es idempotente.

    El nivel se toma de la variable de entorno LOG_LEVEL y, si no existe, de la
    configuración de Flask.
    """
    global _configurado

    raiz = logging.getLogger("app")
    if _configurado:
        return raiz

    if nivel is None:
        nivel = os.getenv("LOG_LEVEL")
    if nivel is None and app is not None:
        nivel = "DEBUG" if app.config.get("DEBUG") else "INFO"
    nivel = (nivel or "INFO").upper()

    raiz.setLevel(nivel)
    raiz.propagate = False

    formateador = logging.Formatter(FORMATO, datefmt=FECHA)

    consola = logging.StreamHandler(sys.stdout)
    consola.setFormatter(formateador)
    raiz.addHandler(consola)

    archivo = os.getenv("LOG_FILE")
    if archivo:
        manejador = logging.handlers.RotatingFileHandler(
            archivo, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        manejador.setFormatter(formateador)
        raiz.addHandler(manejador)

    _configurado = True
    return raiz
