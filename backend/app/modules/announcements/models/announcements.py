from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Aviso(db.Model):
    """Aviso institucional publicado por la dirección."""

    __tablename__ = "avisos"

    id_aviso: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(150))
    contenido: Mapped[str] = mapped_column(Text)
    creado_por: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"))
    publicado_en: Mapped[datetime] = mapped_column(DateTime)
    importante: Mapped[bool] = mapped_column(Boolean)
    estado: Mapped[str] = mapped_column(String(15))


class AvisoDestinatarioRol(db.Model):
    """Roles destinatarios de un aviso."""

    __tablename__ = "avisos_destinatarios_roles"

    id_aviso: Mapped[int] = mapped_column(ForeignKey("avisos.id_aviso"), primary_key=True)
    id_rol: Mapped[int] = mapped_column(SmallInteger, ForeignKey("roles.id_rol"), primary_key=True)


class LecturaAviso(db.Model):
    """Entrega y lectura de un aviso por parte de un usuario."""

    __tablename__ = "lecturas_avisos"

    id_aviso: Mapped[int] = mapped_column(ForeignKey("avisos.id_aviso"), primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), primary_key=True)
    entregado_en: Mapped[datetime | None] = mapped_column(DateTime)
    leido_en: Mapped[datetime | None] = mapped_column(DateTime)
