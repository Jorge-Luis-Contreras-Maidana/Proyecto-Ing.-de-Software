"""Cifrado de los secretos TOTP de cada estudiante."""
import pytest

from app.core.errors.exceptions import InvalidData
from app.core.security.totp_crypto import cifrar, descifrar


@pytest.fixture()
def clave(monkeypatch):
    monkeypatch.setenv("TOTP_ENCRYPTION_KEY", "clave-de-prueba-para-los-tests")
    return "clave-de-prueba-para-los-tests"


def test_el_secreto_va_y_vuelve(clave):
    cifrado = cifrar("JBSWY3DPEHPK3PXP")
    assert cifrado != "JBSWY3DPEHPK3PXP"
    assert descifrar(cifrado) == "JBSWY3DPEHPK3PXP"


def test_el_secreto_cifrado_no_deja_adivinar_el_original(clave):
    cifrado = cifrar("JBSWY3DPEHPK3PXP")
    assert "JBSWY3DPEHPK3PXP" not in cifrado


def test_el_mismo_secreto_cifra_distinto_cada_vez(clave):
    assert cifrar("secreto") != cifrar("secreto")


def test_un_texto_que_no_fue_cifrado_no_se_puede_descifrar(clave):
    with pytest.raises(InvalidData):
        descifrar("DEMO_SECRETO_CIFRADO_0001")


def test_otra_clave_no_puede_descifrar(clave, monkeypatch):
    cifrado = cifrar("secreto")
    monkeypatch.setenv("TOTP_ENCRYPTION_KEY", "otra-clave-distinta")
    with pytest.raises(InvalidData):
        descifrar(cifrado)
