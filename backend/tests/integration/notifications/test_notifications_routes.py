"""Notificaciones: cada usuario solo ve las suyas."""
import pytest
from sqlalchemy import text

from app.extensions import db
from tests.conftest import auth_header


@pytest.fixture()
def director(client, login):
    return auth_header(login("directora.mquispe"))


@pytest.fixture()
def tutor(client, login):
    return auth_header(login("tutor1"))


def _limpiar_notificaciones_de_prueba() -> None:
    db.session.rollback()
    db.session.execute(text("delete from sesco.notificaciones where titulo like 'PRUEBA-%'"))
    db.session.commit()


def test_la_direccion_notifica_a_un_usuario(client, director, tutor):
    _limpiar_notificaciones_de_prueba()
    respuesta = client.post(
        "/api/notifications",
        json={
            "id_usuario_destinatario": 10,
            "tipo": "aviso",
            "titulo": "PRUEBA-Notificación de prueba",
            "mensaje": "Contenido de la notificación.",
        },
        headers=director,
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.get_json()
    assert cuerpo["titulo"] == "PRUEBA-Notificación de prueba"
    assert cuerpo["estado"] == "entregada"
    assert cuerpo["leida_en"] is None


def test_el_usuario_ve_sus_notificaciones(client, director, tutor):
    _limpiar_notificaciones_de_prueba()
    client.post(
        "/api/notifications",
        json={
            "id_usuario_destinatario": 10,
            "tipo": "aviso",
            "titulo": "PRUEBA-Visible para el tutor",
            "mensaje": "Contenido.",
        },
        headers=director,
    )
    listado = client.get("/api/notifications", headers=tutor).get_json()
    assert any(n["titulo"] == "PRUEBA-Visible para el tutor" for n in listado["items"])
    assert listado["no_leidas"] >= 1


def test_el_usuario_marca_una_notificacion_como_leida(client, director, tutor):
    _limpiar_notificaciones_de_prueba()
    creada = client.post(
        "/api/notifications",
        json={
            "id_usuario_destinatario": 10,
            "tipo": "aviso",
            "titulo": "PRUEBA-Para marcar leida",
            "mensaje": "Contenido.",
        },
        headers=director,
    ).get_json()

    leida = client.put(f"/api/notifications/{creada['id_notificacion']}/leer", headers=tutor)
    assert leida.status_code == 200
    assert leida.get_json()["leida_en"] is not None
    assert leida.get_json()["estado"] == "leida"


def test_marcar_todas_como_leidas(client, director, tutor):
    _limpiar_notificaciones_de_prueba()
    for i in range(2):
        client.post(
            "/api/notifications",
            json={
                "id_usuario_destinatario": 10,
                "tipo": "aviso",
                "titulo": f"PRUEBA-Varias {i}",
                "mensaje": "Contenido.",
            },
            headers=director,
        )
    respuesta = client.put("/api/notifications/leer-todas", headers=tutor)
    assert respuesta.status_code == 200
    assert respuesta.get_json()["actualizadas"] >= 1
    assert client.get("/api/notifications/no-leidas", headers=tutor).get_json()["no_leidas"] == 0


def test_no_se_puede_marcar_una_notificacion_ajena(client, director):
    _limpiar_notificaciones_de_prueba()
    creada = client.post(
        "/api/notifications",
        json={
            "id_usuario_destinatario": 10,
            "tipo": "aviso",
            "titulo": "PRUEBA-De otro usuario",
            "mensaje": "Contenido.",
        },
        headers=director,
    ).get_json()

    otro = client.put(f"/api/notifications/{creada['id_notificacion']}/leer", headers=director)
    assert otro.status_code == 404


def test_un_docente_no_crea_notificaciones(client, login):
    headers = auth_header(login("prof.cmamani"))
    respuesta = client.post(
        "/api/notifications",
        json={
            "id_usuario_destinatario": 10,
            "tipo": "aviso",
            "titulo": "PRUEBA-No permitido",
            "mensaje": "x",
        },
        headers=headers,
    )
    assert respuesta.status_code == 403
