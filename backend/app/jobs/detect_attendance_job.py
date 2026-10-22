"""Tarea programada: detección de alertas de inasistencia.

Reutiliza el detector de patrones del módulo de seguimiento para generar las
alertas que falten a partir de las asistencias de la gestión activa.
"""
import logging

log = logging.getLogger(__name__)


def detectar_alertas(app) -> dict:
    """Detecta patrones de inasistencia y crea las alertas nuevas.

    Devuelve un resumen con cuántas alertas se crearon y cuántas se omitieron
    por existir ya una alerta viva del mismo tipo y estudiante.
    """
    from app.modules.followup.services.followup_service import FollowupService

    with app.app_context():
        try:
            creadas, omitidas = FollowupService().detectar()
        except Exception:
            log.exception("No se pudo completar la detección de alertas de asistencia.")
            return {"creadas": 0, "omitidas": 0, "error": True}
        log.info(
            "Detección de alertas de asistencia: %s nuevas, %s ya existentes.",
            len(creadas),
            omitidas,
        )
        return {"creadas": len(creadas), "omitidas": omitidas, "error": False}
