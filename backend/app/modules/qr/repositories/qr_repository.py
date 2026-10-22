from sqlalchemy import select

from app.extensions import db
from app.modules.qr.models.qr import CredencialQR, LecturaQR


class QRRepository:
    def get_credential(self, id_credencial: int) -> CredencialQR | None:
        return db.session.get(CredencialQR, id_credencial)

    def active_credential(self, id_estudiante: int) -> CredencialQR | None:
        stmt = (
            select(CredencialQR)
            .where(CredencialQR.id_estudiante == id_estudiante, CredencialQR.estado == "activa")
            .order_by(CredencialQR.emitida_en.desc())
            .limit(1)
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def add_credential(self, credencial: CredencialQR) -> CredencialQR:
        db.session.add(credencial)
        db.session.flush()
        return credencial

    def read_in_window(self, id_credencial: int, ventana: int) -> LecturaQR | None:
        """Lectura aceptada de esta credencial dentro de la misma ventana TOTP."""
        stmt = select(LecturaQR).where(
            LecturaQR.id_credencial == id_credencial,
            LecturaQR.ventana_totp == ventana,
            LecturaQR.resultado == "aceptado",
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def read_of_asistencia(self, id_asistencia: int) -> LecturaQR | None:
        """Lectura asociada a una asistencia. La tabla permite una sola por asistencia."""
        stmt = select(LecturaQR).where(LecturaQR.id_asistencia == id_asistencia)
        return db.session.execute(stmt).scalar_one_or_none()

    def add_read(self, lectura: LecturaQR) -> LecturaQR:
        db.session.add(lectura)
        db.session.flush()
        return lectura
