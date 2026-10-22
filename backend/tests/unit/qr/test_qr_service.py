"""La ventana TOTP y la detección de la ventana a la que pertenece un código."""
import time

import pyotp

from app.modules.qr.services.totp_service import INTERVALO, TOTPService


def test_el_secreto_generado_tiene_32_caracteres():
    assert len(TOTPService.generate_secret()) == 32


def test_el_secreto_generado_es_distinto():
    assert TOTPService.generate_secret() != TOTPService.generate_secret()


def test_el_codigo_actual_tiene_seis_digitos():
    codigo, ttl = TOTPService.get_current_code_and_ttl(TOTPService.generate_secret())
    assert len(codigo) == 6 and codigo.isdigit()
    assert 0 < ttl <= INTERVALO


def test_la_ventana_actual_cuadra_con_el_codigo():
    secreto = TOTPService.generate_secret()
    assert TOTPService.ventana_del_codigo(secreto, pyotp.TOTP(secreto, interval=INTERVALO).now()) is not None


def test_la_ventana_del_codigo_es_la_del_propio_codigo():
    """El código se asocia a su ventana, no a la del reloj: así no se puede reutilizar."""
    secreto = TOTPService.generate_secret()
    totp = pyotp.TOTP(secreto, interval=INTERVALO)
    codigo = totp.at(time.time() - INTERVALO)
    ventana = TOTPService.ventana_del_codigo(secreto, codigo)
    assert ventana == int((time.time() - INTERVALO) // INTERVALO)


def test_un_codigo_invalido_no_tiene_ventana():
    secreto = TOTPService.generate_secret()
    assert TOTPService.ventana_del_codigo(secreto, "000000") is None


def test_un_codigo_muy_viejo_no_tiene_ventana():
    secreto = TOTPService.generate_secret()
    totp = pyotp.TOTP(secreto, interval=INTERVALO)
    assert TOTPService.ventana_del_codigo(secreto, totp.at(time.time() - 600)) is None


def test_la_ventana_actual_es_un_entero():
    assert isinstance(TOTPService.current_window(), int)
