"""Acceso a datos de la bitácora de auditoría. No aplica reglas de negocio."""
from datetime import datetime, time

from sqlalchemy import func, select

from app.extensions import db
from app.modules.audit.models.audit import EventoAuditoria


class AuditRepository:
    # ---------- consultas ----------
    def get(self, id_evento: int) -> EventoAuditoria | None:
        return db.session.get(EventoAuditoria, id_evento)

    def listar(self, operacion, entidad, id_usuario, desde, hasta, page, per_page):
        conds = []
        if operacion:
            conds.append(func.lower(EventoAuditoria.operacion) == operacion.lower())
        if entidad:
            conds.append(func.lower(EventoAuditoria.entidad) == entidad.lower())
        if id_usuario:
            conds.append(EventoAuditoria.id_usuario == id_usuario)
        if desde:
            conds.append(EventoAuditoria.fecha_hora >= datetime.combine(desde, time.min))
        if hasta:
            conds.append(EventoAuditoria.fecha_hora <= datetime.combine(hasta, time.max))
        total = db.session.scalar(select(func.count()).select_from(EventoAuditoria).where(*conds))
        stmt = (
            select(EventoAuditoria)
            .where(*conds)
            .order_by(EventoAuditoria.fecha_hora.desc(), EventoAuditoria.id_evento.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        return db.session.execute(stmt).scalars().all(), total

    # ---------- escritura ----------
    def add(self, evento: EventoAuditoria) -> EventoAuditoria:
        db.session.add(evento)
        db.session.flush()
        return evento
