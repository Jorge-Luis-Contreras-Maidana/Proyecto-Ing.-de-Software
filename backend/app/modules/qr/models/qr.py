from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class CredencialQR(db.Model):
    """Credencial TOTP de un estudiante. Solo una activa por estudiante."""

    __tablename__ = "credenciales_qr"

    id_credencial: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_estudiante: Mapped[int] = mapped_column(ForeignKey("estudiantes.id_estudiante"))
    secreto_totp_cifrado: Mapped[str] = mapped_column(Text)
    emitida_en: Mapped[datetime] = mapped_column(DateTime)
    revocada_en: Mapped[datetime | None] = mapped_column(DateTime)
    estado: Mapped[str] = mapped_column(String(15))


class LecturaQR(db.Model):
    """Lectura del QR de un estudiante.

    El índice único (id_credencial, ventana_totp) para lecturas aceptadas es lo
    que impide reutilizar el mismo código dentro de la misma ventana de 20 s.
    """

    __tablename__ = "lecturas_qr"

    id_lectura: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_credencial: Mapped[int] = mapped_column(ForeignKey("credenciales_qr.id_credencial"))
    id_asistencia: Mapped[int | None] = mapped_column(ForeignKey("asistencias.id_asistencia"))
    ventana_totp: Mapped[int] = mapped_column(BigInteger)
    leido_en: Mapped[datetime] = mapped_column(DateTime)
    resultado: Mapped[str] = mapped_column(String(20))
    motivo_rechazo: Mapped[str | None] = mapped_column(Text)
    huella_codigo: Mapped[str | None] = mapped_column(String(128))
