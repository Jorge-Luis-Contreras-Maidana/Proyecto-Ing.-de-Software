"""Registro de eventos en la bitácora de auditoría.

Uso previsto desde cualquier módulo:

    from app.modules.audit.services.audit_logger import AuditLogger

    AuditLogger().registrar(
        principal.id_usuario, "CREAR_AVISO", "avisos", str(aviso.id_aviso), "Aviso creado."
    )

La auditoría nunca debe romper la operación principal: si el registro falla,
el error queda en el log y la operación sigue su curso.
"""
import ipaddress
import logging

from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.modules.audit.models.audit import EventoAuditoria
from app.modules.audit.repositories.audit_repository import AuditRepository

log = logging.getLogger(__name__)

# Longitudes máximas de las columnas de la tabla bitacora_auditoria.
MAX_OPERACION = 50
MAX_ENTIDAD = 60
MAX_ID_REGISTRO = 80


def _texto(valor, maximo: int) -> str | None:
    """Recorta el texto para que siempre quepa en la columna."""
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto:
        return None
    return texto[:maximo]


def _direccion_ip(direccion_ip: str | None) -> str | None:
    """Valida la dirección IP; si no es válida se descarta para no perder el evento."""
    if not direccion_ip:
        return None
    try:
        ipaddress.ip_address(str(direccion_ip).strip())
    except ValueError:
        log.warning("Dirección IP inválida para la auditoría: %s", direccion_ip)
        return None
    return str(direccion_ip).strip()


class AuditLogger:
    """Escribe en bitacora_auditoria sin poner en riesgo la operación principal."""

    def __init__(self, repo=None):
        self.repo = repo or AuditRepository()

    def registrar(
        self,
        id_usuario: int | None,
        operacion: str,
        entidad: str,
        id_registro: str | None = None,
        detalle: str | None = None,
        direccion_ip: str | None = None,
    ) -> None:
        """Registra un evento. Si algo falla, se informa en el log y no se interrumpe la operación."""
        try:
            with unit_of_work():
                self.repo.add(
                    EventoAuditoria(
                        id_usuario=id_usuario,
                        operacion=_texto(operacion, MAX_OPERACION) or "OPERACION",
                        entidad=_texto(entidad, MAX_ENTIDAD) or "desconocida",
                        id_registro=_texto(id_registro, MAX_ID_REGISTRO),
                        fecha_hora=clock.now(),
                        direccion_ip=_direccion_ip(direccion_ip),
                        detalle=detalle,
                    )
                )
        except Exception:  # noqa: BLE001 - la auditoría no debe romper la operación principal
            log.exception("No se pudo registrar el evento de auditoría '%s' sobre '%s'.", operacion, entidad)
