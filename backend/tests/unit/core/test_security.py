from datetime import datetime, timedelta

from app.core.security.hashing import hash_password, verify_password
from app.core.security.rbac import has_any_role
from app.core.security.session_policy import is_expired, new_expiry


def test_la_contrasena_se_guarda_con_hash_y_se_verifica():
    h = hash_password("Secreta123")
    assert h != "Secreta123" and h.startswith("$argon2")
    assert verify_password(h, "Secreta123") is True
    assert verify_password(h, "otra") is False


def test_un_hash_invalido_no_rompe_la_verificacion():
    assert verify_password("DEMO_HASH_CAMBIAR_EN_APLICACION", "lo-que-sea") is False


def test_roles():
    assert has_any_role(("profesor",), ("director", "profesor")) is True
    assert has_any_role(("tutor",), ("director",)) is False
    assert has_any_role(("tutor",), ()) is True


def test_la_sesion_expira_a_los_15_minutos():
    inicio = datetime(2026, 3, 2, 8, 0)
    limite = new_expiry(inicio, 15)
    assert limite == datetime(2026, 3, 2, 8, 15)
    assert is_expired(limite, inicio + timedelta(minutes=14)) is False
    assert is_expired(limite, inicio + timedelta(minutes=15)) is True
