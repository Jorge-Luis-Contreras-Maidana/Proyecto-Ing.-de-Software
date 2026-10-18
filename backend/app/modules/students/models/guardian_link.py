from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Tutor(db.Model):
    __tablename__ = "tutores"

    id_tutor: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(Integer, unique=True)
    documento_identidad: Mapped[str | None] = mapped_column(String(30))
    estado: Mapped[str] = mapped_column(String(15))


class EstudianteTutor(db.Model):
    """Vínculo entre un estudiante y su padre o tutor. Solo vale cuando el director lo confirma (RD-02.2)."""

    __tablename__ = "estudiante_tutor"

    id_estudiante: Mapped[int] = mapped_column(ForeignKey("estudiantes.id_estudiante"), primary_key=True)
    id_tutor: Mapped[int] = mapped_column(ForeignKey("tutores.id_tutor"), primary_key=True)
    parentesco: Mapped[str] = mapped_column(String(30))
    es_contacto_principal: Mapped[bool] = mapped_column(Boolean)
    confirmado: Mapped[bool] = mapped_column(Boolean)
    confirmado_por: Mapped[int | None] = mapped_column(Integer)
    confirmado_en: Mapped[datetime | None] = mapped_column(DateTime)