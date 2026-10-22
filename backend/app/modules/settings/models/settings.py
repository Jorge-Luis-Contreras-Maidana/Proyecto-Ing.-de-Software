from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class ConfiguracionAsistencia(db.Model):
    """Parámetros de la unidad educativa que gobiernan la clasificación de la asistencia.

    Los valores por defecto coinciden con los del RF y con lo que define el
    administrador en la pantalla de configuración.
    """

    __tablename__ = "configuracion_asistencia"

    id_configuracion: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_unidad: Mapped[int] = mapped_column(ForeignKey("unidades_educativas.id_unidad"))
    tolerancia_ingreso_min: Mapped[int] = mapped_column(SmallInteger)
    limite_tardanza_min: Mapped[int] = mapped_column(SmallInteger)
    ausencias_consecutivas_alerta: Mapped[int] = mapped_column(SmallInteger)
    tardanzas_mes_alerta: Mapped[int] = mapped_column(SmallInteger)
    porcentaje_ausencia_alerta: Mapped[float] = mapped_column(Numeric(5, 2))
    plazo_justificacion_dias: Mapped[int] = mapped_column(SmallInteger)
    actualizado_en: Mapped[datetime | None] = mapped_column(DateTime)
    actualizado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"))
