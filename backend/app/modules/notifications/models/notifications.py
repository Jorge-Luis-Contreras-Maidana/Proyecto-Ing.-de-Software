from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Notificacion(db.Model):
    """Notificación dirigida a un usuario concreto."""

    __tablename__ = "notificaciones"

    id_notificacion: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_usuario_destinatario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"))
    tipo: Mapped[str] = mapped_column(String(35))
    titulo: Mapped[str] = mapped_column(String(150))
    mensaje: Mapped[str] = mapped_column(Text)
    creada_en: Mapped[datetime] = mapped_column(DateTime)
    entregada_en: Mapped[datetime | None] = mapped_column(DateTime)
    leida_en: Mapped[datetime | None] = mapped_column(DateTime)
    estado: Mapped[str] = mapped_column(String(15))
    entidad_referencia: Mapped[str | None] = mapped_column(String(40))
    id_referencia: Mapped[int | None] = mapped_column(BigInteger)
