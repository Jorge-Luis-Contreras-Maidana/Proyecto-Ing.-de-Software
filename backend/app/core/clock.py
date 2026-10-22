"""Hora oficial de Bolivia (UTC-4). RD-01.3.

Toda la aplicación debe usar clock.now() en lugar de datetime.now().
Devuelve un datetime sin zona horaria, coherente con las columnas TIMESTAMP de la base.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

BOLIVIA_TZ = ZoneInfo("America/La_Paz")


def now() -> datetime:
    return datetime.now(BOLIVIA_TZ).replace(tzinfo=None)
