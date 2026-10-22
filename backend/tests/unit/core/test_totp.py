import time

import pyotp
import pytest

from app.modules.qr.services.totp_service import TOTPService


def test_generate_totp_secret_length():
    secret = TOTPService.generate_secret()
    assert len(secret) == 32

def test_verify_valid_totp_code():
    secret = TOTPService.generate_secret()
    totp = pyotp.TOTP(secret, interval=20)
    current_code = totp.now()

    assert TOTPService.verify_code(secret, current_code) is True

def test_verify_invalid_totp_code():
    secret = TOTPService.generate_secret()
    assert TOTPService.verify_code(secret, "000000") is False

def test_totp_window_tolerance():
    secret = TOTPService.generate_secret()
    totp = pyotp.TOTP(secret, interval=20)
    # Genera el código para la ventana previa (-20s)
    past_code = totp.at(time.time() - 20)
    assert TOTPService.verify_code(secret, past_code) is True

def test_totp_expired_code():
    secret = TOTPService.generate_secret()
    totp = pyotp.TOTP(secret, interval=20)
    # Genera un código fuera de la ventana de tolerancia de ±1 (hace 60s)
    old_code = totp.at(time.time() - 60)
    assert TOTPService.verify_code(secret, old_code) is False
