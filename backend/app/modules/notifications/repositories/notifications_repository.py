"""Acceso a datos de las notificaciones. No aplica reglas de negocio."""
from sqlalchemy import func, select, update

from app.extensions import db
from app.modules.notifications.models.notifications import Notificacion


class NotificationsRepository:
    # ---------- consultas ----------
    def get(self, id_notificacion: int) -> Notificacion | None:
        return db.session.get(Notificacion, id_notificacion)

    def listar(self, id_usuario: int, page: int, per_page: int):
        base = select(Notificacion).where(Notificacion.id_usuario_destinatario == id_usuario)
        total = db.session.scalar(
            select(func.count()).select_from(Notificacion).where(
                Notificacion.id_usuario_destinatario == id_usuario
            )
        )
        stmt = (
            base.order_by(Notificacion.creada_en.desc(), Notificacion.id_notificacion.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        return db.session.execute(stmt).scalars().all(), total

    def contar_no_leidas(self, id_usuario: int) -> int:
        stmt = select(func.count()).select_from(Notificacion).where(
            Notificacion.id_usuario_destinatario == id_usuario,
            Notificacion.estado != "leida",
        )
        return int(db.session.scalar(stmt) or 0)

    # ---------- escritura ----------
    def add(self, notificacion: Notificacion) -> Notificacion:
        db.session.add(notificacion)
        db.session.flush()
        return notificacion

    def marcar_todas_leidas(self, id_usuario: int, leida_en) -> int:
        """Marca como leídas todas las notificaciones pendientes del usuario."""
        stmt = (
            update(Notificacion)
            .where(
                Notificacion.id_usuario_destinatario == id_usuario,
                Notificacion.estado != "leida",
            )
            .values(estado="leida", leida_en=leida_en)
        )
        return int(db.session.execute(stmt).rowcount or 0)
