"""Reglas de negocio de la bitácora de auditoría. No usa Flask ni escribe SQL."""
from app.core.errors.exceptions import InvalidData, NotFound
from app.core.security.rbac import Principal
from app.modules.audit.models.audit import EventoAuditoria
from app.modules.audit.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, repo=None):
        self.repo = repo or AuditRepository()

    def listar(
        self,
        principal: Principal,
        operacion=None,
        entidad=None,
        id_usuario=None,
        desde=None,
        hasta=None,
        page=1,
        per_page=50,
    ):
        """Listado paginado de eventos, con los filtros indicados en la API."""
        if desde and hasta and desde > hasta:
            raise InvalidData(
                "La fecha inicial no puede ser posterior a la fecha final.",
                "Corrija el rango de fechas e intente nuevamente.",
            )
        return self.repo.listar(operacion, entidad, id_usuario, desde, hasta, page, per_page)

    def obtener(self, principal: Principal, id_evento: int) -> EventoAuditoria:
        evento = self.repo.get(id_evento)
        if evento is None:
            raise NotFound("No se encontró el evento de auditoría.", "Verifique el evento o regrese al inicio.")
        return evento
