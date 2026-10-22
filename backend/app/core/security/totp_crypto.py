"""Cifrado de los secretos TOTP de cada estudiante.

El secreto nunca se guarda en claro: se cifra con Fernet (AES-128-CBC + HMAC)
usando la clave TOTP_ENCRYPTION_KEY. Así, si alguien lee la base de datos no
puede suplantar el QR de un estudiante.

La clave se toma del entorno, no de la configuración de Flask, para que este
módulo no dependa del framework web.
"""
import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken

from app.core.errors.exceptions import InvalidData

CLAVE_POR_DEFECTO = "cambia_esto"


def _clave() -> bytes:
    """Deriva una clave Fernet válida a partir de TOTP_ENCRYPTION_KEY."""
    secreto = os.getenv("TOTP_ENCRYPTION_KEY") or CLAVE_POR_DEFECTO
    return base64.urlsafe_b64encode(hashlib.sha256(secreto.encode("utf-8")).digest())


def cifrar(texto: str) -> str:
    """Cifra un texto y devuelve el resultado en base64url."""
    return Fernet(_clave()).encrypt(texto.encode("utf-8")).decode("utf-8")


def descifrar(cifrado: str) -> str:
    """Revierte cifrar(). Lanza InvalidData si el texto no se puede descifrar."""
    try:
        return Fernet(_clave()).decrypt(cifrado.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError) as err:
        raise InvalidData(
            "La credencial del estudiante no se pudo descifrar.",
            "Solicite a la dirección que reemita la credencial QR.",
        ) from err
