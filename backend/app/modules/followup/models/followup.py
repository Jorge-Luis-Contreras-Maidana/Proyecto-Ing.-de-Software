from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class AlertaAsistencia(db.Model):
    """Alerta de seguimiento detectada por el sistema o registrada a mano."""

    __tablename__ = "alertas_asistencia"

    id_alerta: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_estudiante: Mapped[int] = mapped_column(ForeignKey("estudiantes.id_estudiante"))
    id_curso: Mapped[int] = mapped_column(ForeignKey("cursos.id_curso"))
    tipo: Mapped[str] = mapped_column(String(30))
    descripcion: Mapped[str] = mapped_column(Text)
    generada_en: Mapped[datetime] = mapped_column(DateTime)
    estado: Mapped[str] = mapped_column(String(20))
    asignada_a: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"))
    resuelta_en: Mapped[datetime | None] = mapped_column(DateTime)
    observacion: Mapped[str | None] = mapped_column(Text)
