"""Política de sesión: cierre automático tras 15 minutos de inactividad. RNF-02.3."""
from datetime import datetime, timedelta


def new_expiry(now: datetime, idle_minutes: int) -> datetime:
    return now + timedelta(minutes=idle_minutes)


def is_expired(expires_at: datetime, now: datetime) -> bool:
    return expires_at <= now
