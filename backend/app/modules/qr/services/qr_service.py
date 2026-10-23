"""Emisión y verificación de la credencial QR de cada estudiante.

Cada estudiante tiene su propio secreto TOTP, cifrado en la base de datos
(ver app.core.security.totp_crypto). Un código solo sirve para el estudiante
que lo emitió, y cada lectura queda registrada en 'lecturas_qr' para poder
auditar y para impedir que el mismo código se acepte dos veces en la misma
ventana de 20 segundos.
"""
import base64
import io
import json
from dataclasses import dataclass

import qrcode
from sqlalchemy import select

from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.core.errors.exceptions import InvalidData, NotFound
from app.core.security.totp_crypto import cifrar, descifrar
from app.extensions import db
from app.modules.qr.models.qr import CredencialQR, LecturaQR
from app.modules.qr.repositories.qr_repository import QRRepository
from app.modules.qr.services.totp_service import INTERVALO, TOTPService
from app.modules.students.models.students import Estudiante

# Roles que pueden ver la credencial de un estudiante concreto.
_PUEDEN_VER_CUALQUIER = ("director", "profesor")


@dataclass(frozen=True)
class QRCodeResult:
    id_estudiante: int
    code: str
    expires_in: int
    imagen_base64: str
    id_credencial: int


class QRService:
    def __init__(self, repo=None):
        self.repo = repo or QRRepository()

    # ---------- emisión ----------
    def emitir_si_falta(self, id_estudiante: int) -> CredencialQR:
        """Devuelve la credencial activa del estudiante; si no tiene, le emite una.

        También la reemite cuando el secreto guardado no se puede descifrar: eso
        pasa cuando rota la clave TOTP_ENCRYPTION_KEY o cuando el dato se daña.
        Una credencial así no sirve para nada, y dejarla tal cual haría fallar
        cada vez que el estudiante abre su QR, así que se revoca y se emite otra.
        """
        actual = self.repo.active_credential(id_estudiante)
        if actual is not None and self._secreto_descifrable(actual):
            return actual
        with unit_of_work():
            if actual is not None:
                actual.estado = "revocada"
                actual.revocada_en = clock.now()
            return self.repo.add_credential(
                CredencialQR(
                    id_estudiante=id_estudiante,
                    secreto_totp_cifrado=cifrar(TOTPService.generate_secret()),
                    emitida_en=clock.now(),
                    estado="activa",
                )
            )

    @staticmethod
    def _secreto_descifrable(credencial: CredencialQR) -> bool:
        """False si el secreto cifrado no se puede revertir con la clave actual."""
        try:
            descifrar(credencial.secreto_totp_cifrado)
        except InvalidData:
            return False
        return True

    def renovar_credencial(self, principal, id_estudiante: int) -> QRCodeResult:
        """El director invalida la credencial anterior y emite una nueva."""
        anterior = self.repo.active_credential(id_estudiante)
        with unit_of_work():
            if anterior is not None:
                anterior.estado = "revocada"
                anterior.revocada_en = clock.now()
            nueva = self.repo.add_credential(
                CredencialQR(
                    id_estudiante=id_estudiante,
                    secreto_totp_cifrado=cifrar(TOTPService.generate_secret()),
                    emitida_en=clock.now(),
                    estado="activa",
                )
            )
        return self._codigo_para(nueva)

    # ---------- lectura ----------
    def _codigo_para(self, credencial: CredencialQR) -> QRCodeResult:
        secreto = descifrar(credencial.secreto_totp_cifrado)
        code, expires_in = TOTPService.get_current_code_and_ttl(secreto)
        contenido = json.dumps(
            {
                "id_estudiante": credencial.id_estudiante,
                "code": code,
                "ventana": TOTPService.current_window(),
            },
            separators=(",", ":"),
        )
        imagen = qrcode.make(contenido)
        buffer = io.BytesIO()
        imagen.save(buffer, format="PNG")
        return QRCodeResult(
            id_estudiante=credencial.id_estudiante,
            code=code,
            expires_in=expires_in,
            imagen_base64=base64.b64encode(buffer.getvalue()).decode("utf-8"),
            id_credencial=credencial.id_credencial,
        )

    def codigo_del_estudiante(self, principal, id_estudiante: int) -> QRCodeResult:
        """Credencial QR. Un estudiante solo puede ver la suya; el personal, la de quien sea."""
        es_personal = bool(set(principal.roles) & set(_PUEDEN_VER_CUALQUIER))
        if not es_personal:
            propio = self._id_estudiante_del_usuario(principal.id_usuario)
            if propio != id_estudiante:
                raise NotFound(
                    "No encontró la credencial del estudiante.",
                    "Verifique el estudiante o regrese al inicio.",
                )
        credencial = self.emitir_si_falta(id_estudiante)
        return self._codigo_para(credencial)

    @staticmethod
    def _id_estudiante_del_usuario(id_usuario: int) -> int | None:
        stmt = select(Estudiante.id_estudiante).where(Estudiante.id_usuario == id_usuario)
        return db.session.execute(stmt).scalar_one_or_none()

    # ---------- verificación ----------
    def verificar(self, principal, id_estudiante: int, codigo: str) -> dict:
        """Valida el código QR de un estudiante.

        Un código expirado o ya usado se registra en 'lecturas_qr' con su motivo
        y se rechaza con un error 422.
        """
        credencial = self.repo.active_credential(id_estudiante)
        if credencial is None:
            raise NotFound(
                "El estudiante no tiene una credencial QR activa.",
                "Solicite a la dirección que emita una credencial.",
            )

        secreto = descifrar(credencial.secreto_totp_cifrado)

        # La ventana es la del propio código: así el mismo código no puede
        # aceptarse dos veces, aunque se escanee dentro o fuera de su ventana.
        ventana = TOTPService.ventana_del_codigo(secreto, codigo)
        if ventana is None:
            with unit_of_work():
                self.repo.add_read(
                    LecturaQR(
                        id_credencial=credencial.id_credencial,
                        ventana_totp=TOTPService.current_window(),
                        leido_en=clock.now(),
                        resultado="expirado",
                        motivo_rechazo="El código no corresponde a ninguna ventana TOTP válida.",
                    )
                )
            raise InvalidData(
                "El código QR expiró o no es válido.",
                "Pida al estudiante que actualice su credencial e intente nuevamente.",
            )

        if self.repo.read_in_window(credencial.id_credencial, ventana) is not None:
            with unit_of_work():
                self.repo.add_read(
                    LecturaQR(
                        id_credencial=credencial.id_credencial,
                        ventana_totp=ventana,
                        leido_en=clock.now(),
                        resultado="duplicado",
                        motivo_rechazo="El código ya se aceptó en esta misma ventana.",
                    )
                )
            raise InvalidData(
                "Ese código QR ya se usó.",
                "Espere a que se renueve el código e intente nuevamente.",
            )

        return {
            "id_credencial": credencial.id_credencial,
            "id_estudiante": id_estudiante,
            "ventana_totp": ventana,
        }

    def tiene_lectura(self, id_asistencia: int) -> bool:
        """True si esa asistencia ya tiene una lectura de QR registrada."""
        return self.repo.read_of_asistencia(id_asistencia) is not None

    def registrar_lectura(
        self,
        id_credencial: int,
        ventana: int,
        id_asistencia: int | None,
        resultado: str = "aceptado",
        motivo: str | None = None,
    ) -> LecturaQR:
        """Registra la lectura. No abre transacción: la controla quien la llama."""
        return self.repo.add_read(
            LecturaQR(
                id_credencial=id_credencial,
                id_asistencia=id_asistencia,
                ventana_totp=ventana,
                leido_en=clock.now(),
                resultado=resultado,
                motivo_rechazo=motivo,
            )
        )


def contenido_del_codigo(contenido: str) -> dict:
    """Interpreta el texto del QR: acepta el JSON emitido por la app y un código suelto."""
    try:
        datos = json.loads(contenido)
    except (ValueError, TypeError):
        return {"code": (contenido or "").strip(), "id_estudiante": None}
    if not isinstance(datos, dict):
        return {"code": (contenido or "").strip(), "id_estudiante": None}
    return {
        "code": str(datos.get("code", "")),
        "id_estudiante": datos.get("id_estudiante"),
    }


__all__ = ["QRService", "QRCodeResult", "contenido_del_codigo", "INTERVALO"]
