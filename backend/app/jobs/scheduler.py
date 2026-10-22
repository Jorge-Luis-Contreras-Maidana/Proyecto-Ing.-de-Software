"""Planificador de tareas periódicas (APScheduler).

El planificador se enciende con la variable de configuración SCHEDULER_ENABLED:
por defecto está apagado en desarrollo y encendido en producción. La instancia
vive en este módulo para que init_scheduler no pueda arrancar dos veces.
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.jobs.detect_attendance_job import detectar_alertas
from app.jobs.purge_audit_job import purgar_auditoria

log = logging.getLogger(__name__)

# Hora oficial de la unidad educativa (RD-01.3).
ZONA_HORARIA = "America/La_Paz"

# Instancia viva del planificador: evita arrancar dos veces.
_scheduler: BackgroundScheduler | None = None


def planificador_activo(app) -> bool:
    """True si la configuración de la aplicación permite arrancar el planificador."""
    valor = app.config.get("SCHEDULER_ENABLED")
    if valor is None:
        # Sin configuración explícita solo se activa en producción.
        valor = app.config.get("ENV_NAME") == "production"
    return bool(valor)


def init_scheduler(app):
    """Crea y arranca el planificador de tareas.

    Devuelve el planificador o None cuando está desactivado por configuración.
    Si ya hay uno activo, no se vuelve a arrancar.
    """
    global _scheduler
    if _scheduler is not None:
        log.info("El planificador ya estaba iniciado; no se arranca de nuevo.")
        return _scheduler

    if not planificador_activo(app):
        log.info("Planificador desactivado por configuración (SCHEDULER_ENABLED).")
        return None

    scheduler = BackgroundScheduler(timezone=ZONA_HORARIA, daemon=True)
    scheduler.add_job(
        detectar_alertas,
        "cron",
        hour=7,
        minute=0,
        args=[app],
        id="detectar_alertas_asistencia",
        replace_existing=True,
        coalesce=True,
        misfire_grace_time=3600,
    )
    scheduler.add_job(
        purgar_auditoria,
        "cron",
        hour=2,
        minute=30,
        args=[app],
        id="purgar_auditoria",
        replace_existing=True,
        coalesce=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    _scheduler = scheduler
    log.info("Planificador iniciado: detección de alertas y purga de auditoría.")
    return scheduler


def get_scheduler() -> BackgroundScheduler | None:
    """Planificador activo, si lo hay."""
    return _scheduler


def shutdown_scheduler() -> None:
    """Detiene el planificador (para las pruebas y el cierre de la aplicación)."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
