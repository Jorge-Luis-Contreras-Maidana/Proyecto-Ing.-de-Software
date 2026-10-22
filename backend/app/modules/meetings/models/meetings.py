from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Citacion(db.Model):
    """Citación a un tutor para revisar el seguimiento de un estudiante."""

    __tablename__ = "citaciones"

    id_citacion: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_estudiante: Mapped[int] = mapped_column(ForeignKey("estudiantes.id_estudiante"))
    id_tutor: Mapped[int] = mapped_column(ForeignKey("tutores.id_tutor"))
    id_profesor: Mapped[int] = mapped_column(ForeignKey("profesores.id_profesor"))
    id_alerta: Mapped[int | None] = mapped_column(ForeignKey("alertas_asistencia.id_alerta"))
    fecha_hora: Mapped[datetime] = mapped_column(DateTime)
    motivo: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(20))
    creada_en: Mapped[datetime] = mapped_column(DateTime)
    observaciones: Mapped[str | None] = mapped_column(Text)
