from datetime import timedelta

from app.core import clock
from tests.conftest import PASSWORD, auth_header


def test_login_correcto_devuelve_token_y_roles(login):
    r = login("directora.mquispe")
    assert r.status_code == 200
    body = r.get_json()
    assert body["access_token"]
    assert body["usuario"]["roles"] == ["director"]
    assert body["inactividad_max_minutos"] == 15
    assert "hash_contrasena" not in str(body)


def test_credenciales_invalidas_rechazan_con_mensaje(login):
    r = login("directora.mquispe", "incorrecta")
    assert r.status_code == 401
    err = r.get_json()["error"]
    assert err["codigo"] == "credenciales_invalidas"
    assert err["mensaje"] and err["accion"]


def test_usuario_inexistente_da_el_mismo_mensaje(login):
    a = login("nadie", "x").get_json()
    b = login("directora.mquispe", "x").get_json()
    assert a == b


def test_faltan_datos(client):
    r = client.post("/api/auth/login", json={"nombre_usuario": "x"})
    assert r.status_code == 422
    assert r.get_json()["error"]["codigo"] == "datos_invalidos"


def test_me_sin_token_pide_iniciar_sesion(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401
    assert r.get_json()["error"]["codigo"] == "no_autenticado"


def test_me_con_token(client, login):
    r = client.get("/api/auth/me", headers=auth_header(login("prof.cmamani")))
    assert r.status_code == 200
    assert r.get_json()["roles"] == ["profesor"]


def test_solo_el_rol_permitido_accede(client, login):
    ok = client.get("/_test/solo-director", headers=auth_header(login("directora.mquispe")))
    assert ok.status_code == 200
    no = client.get("/_test/solo-director", headers=auth_header(login("tutor1")))
    assert no.status_code == 403
    assert no.get_json()["error"]["codigo"] == "sin_permiso"


def test_la_sesion_se_cierra_a_los_15_minutos_de_inactividad(client, login, monkeypatch):
    h = auth_header(login("prof.cmamani"))
    ahora = clock.now()
    monkeypatch.setattr(clock, "now", lambda: ahora + timedelta(minutes=16))
    r = client.get("/api/auth/me", headers=h)
    assert r.status_code == 401
    assert r.get_json()["error"]["codigo"] == "sesion_expirada"


def test_la_actividad_renueva_la_sesion(client, login, monkeypatch):
    h = auth_header(login("prof.cmamani"))
    ahora = clock.now()
    monkeypatch.setattr(clock, "now", lambda: ahora + timedelta(minutes=10))
    assert client.get("/api/auth/me", headers=h).status_code == 200
    monkeypatch.setattr(clock, "now", lambda: ahora + timedelta(minutes=20))
    assert client.get("/api/auth/me", headers=h).status_code == 200  # 10 min tras la última actividad


def test_logout_invalida_la_sesion(client, login):
    h = auth_header(login("tutor1"))
    assert client.post("/api/auth/logout", headers=h).status_code == 200
    r = client.get("/api/auth/me", headers=h)
    assert r.status_code == 401
    assert r.get_json()["error"]["codigo"] == "sesion_cerrada"


def test_peticion_demasiado_grande_se_rechaza(client):
    r = client.post("/api/auth/login", data="x" * (101 * 1024), content_type="application/json")
    assert r.status_code == 413
    assert r.get_json()["error"]["codigo"] == "solicitud_demasiado_grande"


def test_ruta_inexistente_responde_en_formato_estandar(client):
    r = client.get("/api/no-existe")
    assert r.status_code == 404
    assert r.get_json()["error"]["codigo"] == "no_encontrado"


def test_health(client):
    assert client.get("/api/health").get_json() == {"estado": "ok"}