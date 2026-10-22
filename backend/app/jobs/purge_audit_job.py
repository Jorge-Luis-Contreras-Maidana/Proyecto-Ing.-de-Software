"""Tarea programada: purga de los eventos de auditoría antiguos.

La bitácora de auditoría crece sin control; esta tarea borra los eventos que
superan la antigüedad máxima configurada (AUDIT_PURGE_DAYS, 365 días por
defecto).
"""
import logging
from datetime import timedelta

from sqlalchemy import delete

from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.extensions import db
from app.modules.audit.models.audit import EventoAuditoria

log = logging.getLogger(__name__)

# Antigüedad máxima por defecto (en días) de los eventos de auditoría.
DIAS_POR_DEFECTO = 365


def purgar_auditoria(app, dias: int | None = None) -> int:
    """Borra los eventos con más de N días. Devuelve cuántos borró."""
    limite_dias = dias if dias is not None else app.config.get("AUDIT_PURGE_DAYS", DIAS_POR_DEFECTO)
    limite_dias = int(limite_dias)
    with app.app_context():
        limite = clock.now() - timedelta(days=limite_dias)
        with unit_of_work():
            borrados = db.session.execute(
                delete(EventoAuditoria).where(EventoAuditoria.fecha_hora < limite)
            ).rowcount
        log.info(
            "Se borraron %s eventos de auditoría anteriores a %s.", borrados, limite.date()
        )
        return int(borrados or 0)
