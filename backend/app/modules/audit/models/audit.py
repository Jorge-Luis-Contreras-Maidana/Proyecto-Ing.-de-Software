from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class EventoAuditoria(db.Model):
    """Rastro de las operaciones sensibles del sistema."""

    __tablename__ = "bitacora_auditoria"

    id_evento: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_usuario: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"))
    operacion: Mapped[str] = mapped_column(String(50))
    entidad: Mapped[str] = mapped_column(String(60))
    id_registro: Mapped[str | None] = mapped_column(String(80))
    fecha_hora: Mapped[datetime] = mapped_column(DateTime)
    direccion_ip: Mapped[str | None] = mapped_column(INET)
    detalle: Mapped[str | None] = mapped_column(Text)
