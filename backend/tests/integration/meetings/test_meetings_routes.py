"""Citas de seguimiento con los tutores."""
import pytest
from sqlalchemy import text

from app.core import clock
from app.extensions import db
from tests.conftest import auth_header


@pytest.fixture()
def director(client, login):
    return auth_header(login("directora.mquispe"))


@pytest.fixture()
def tutor(client, login):
    return auth_header(login("tutor1"))


def _limpiar_citas_de_prueba() -> None:
    db.session.rollback()
    db.session.execute(text("delete from sesco.citaciones where motivo like 'PRUEBA-%'"))
    db.session.commit()


def test_la_direccion_convoca_una_cita(client, director):
    _limpiar_citas_de_prueba()
    fecha = clock.now().replace(hour=9, minute=0, second=0, microsecond=0)
    respuesta = client.post(
        "/api/meetings",
        json={
            "id_estudiante": 1,
            "id_tutor": 1,
            "id_profesor": 1,
            "fecha_hora": fecha.isoformat(),
            "motivo": "PRUEBA-Cita de seguimiento",
        },
        headers=director,
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.get_json()
    assert cuerpo["estado"] == "programada"
    assert cuerpo["id_estudiante"] == 1
    assert cuerpo["motivo"] == "PRUEBA-Cita de seguimiento"


def test_se_cambia_el_estado_de_una_cita(client, director):
    _limpiar_citas_de_prueba()
    fecha = clock.now().replace(hour=9, minute=0, second=0, microsecond=0)
    creada = client.post(
        "/api/meetings",
        json={
            "id_estudiante": 1,
            "id_tutor": 1,
            "id_profesor": 1,
            "fecha_hora": fecha.isoformat(),
            "motivo": "PRUEBA-Cita para confirmar",
        },
        headers=director,
    ).get_json()

    respuesta = client.put(
        f"/api/meetings/{creada['id_citacion']}/estado",
        json={"estado": "confirmada", "observaciones": "El tutor confirmó."},
        headers=director,
    )
    assert respuesta.status_code == 200
    assert respuesta.get_json()["estado"] == "confirmada"
    assert respuesta.get_json()["observaciones"] == "El tutor confirmó."


def test_el_listado_se_filtra_por_estado(client, director):
    _limpiar_citas_de_prueba()
    fecha = clock.now().replace(hour=9, minute=0, second=0, microsecond=0)
    creada = client.post(
        "/api/meetings",
        json={
            "id_estudiante": 1,
            "id_tutor": 1,
            "id_profesor": 1,
            "fecha_hora": fecha.isoformat(),
            "motivo": "PRUEBA-Cita filtrable",
        },
        headers=director,
    ).get_json()

    listado = client.get(f"/api/meetings?id_estudiante={creada['id_estudiante']}", headers=director).get_json()
    assert creada["id_citacion"] in {c["id_citacion"] for c in listado["items"]}

    por_estado = client.get("/api/meetings?estado=programada", headers=director).get_json()
    assert all(c["estado"] == "programada" for c in por_estado["items"])


def test_un_tutor_no_convoca_citas(client, tutor):
    fecha = clock.now().replace(hour=9, minute=0, second=0, microsecond=0)
    respuesta = client.post(
        "/api/meetings",
        json={
            "id_estudiante": 1,
            "id_tutor": 1,
            "id_profesor": 1,
            "fecha_hora": fecha.isoformat(),
            "motivo": "PRUEBA-No permitido",
        },
        headers=tutor,
    )
    assert respuesta.status_code == 403


def test_sin_datos_obligatorios_se_rechaza(client, director):
    respuesta = client.post("/api/meetings", json={}, headers=director)
    assert respuesta.status_code == 422
