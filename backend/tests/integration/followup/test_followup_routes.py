"""Alertas de seguimiento: alta, cambio de estado y detección de patrones."""
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


def _limpiar_alertas_de_prueba() -> None:
    db.session.rollback()
    db.session.execute(text("delete from sesco.alertas_asistencia where descripcion like 'PRUEBA-%'"))
    db.session.commit()


def test_la_direccion_registra_una_alerta(client, director):
    _limpiar_alertas_de_prueba()
    respuesta = client.post(
        "/api/followup/alertas",
        json={
            "id_estudiante": 1,
            "id_curso": 1,
            "tipo": "otra",
            "descripcion": "PRUEBA-Alerta de seguimiento",
        },
        headers=director,
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.get_json()
    assert cuerpo["tipo"] == "otra"
    assert cuerpo["estado"] == "abierta"
    assert cuerpo["id_estudiante"] == 1


def test_se_cambia_el_estado_de_una_alerta(client, director):
    _limpiar_alertas_de_prueba()
    creada = client.post(
        "/api/followup/alertas",
        json={
            "id_estudiante": 1,
            "id_curso": 1,
            "tipo": "otra",
            "descripcion": "PRUEBA-Alerta para resolver",
        },
        headers=director,
    ).get_json()

    respuesta = client.put(
        f"/api/followup/alertas/{creada['id_alerta']}/estado",
        json={"estado": "resuelta", "observacion": "Se conversó con el tutor."},
        headers=director,
    )
    assert respuesta.status_code == 200
    assert respuesta.get_json()["estado"] == "resuelta"
    assert respuesta.get_json()["observacion"] == "Se conversó con el tutor."


def test_se_filtra_por_estado_y_estudiante(client, director):
    _limpiar_alertas_de_prueba()
    creada = client.post(
        "/api/followup/alertas",
        json={
            "id_estudiante": 1,
            "id_curso": 1,
            "tipo": "otra",
            "descripcion": "PRUEBA-Alerta filtrable",
        },
        headers=director,
    ).get_json()

    listado = client.get(f"/api/followup/alertas?id_estudiante={creada['id_estudiante']}", headers=director).get_json()
    assert creada["id_alerta"] in {a["id_alerta"] for a in listado["items"]}

    por_estado = client.get("/api/followup/alertas?estado=abierta", headers=director).get_json()
    assert all(a["estado"] == "abierta" for a in por_estado["items"])


def test_las_alertas_de_un_estudiante(client, director):
    respuesta = client.get("/api/followup/estudiante/1", headers=director)
    assert respuesta.status_code == 200
    assert "items" in respuesta.get_json()


def test_la_deteccion_de_patrones_responde(client, director):
    respuesta = client.post("/api/followup/detectar", headers=director)
    assert respuesta.status_code == 200
    cuerpo = respuesta.get_json()
    assert "items" in cuerpo
    assert "creadas" in cuerpo


def test_un_docente_tambien_puede_registrar_alertas(client, login):
    """El contrato permite que los docentes registren alertas de seguimiento."""
    _limpiar_alertas_de_prueba()
    headers = auth_header(login("prof.cmamani"))
    respuesta = client.post(
        "/api/followup/alertas",
        json={"id_estudiante": 1, "id_curso": 1, "tipo": "otra", "descripcion": "PRUEBA-Alerta del docente"},
        headers=headers,
    )
    assert respuesta.status_code == 201


def test_un_tutor_no_registra_alertas(client, tutor):
    respuesta = client.post(
        "/api/followup/alertas",
        json={"id_estudiante": 1, "id_curso": 1, "tipo": "otra", "descripcion": "PRUEBA-No permitido"},
        headers=tutor,
    )
    assert respuesta.status_code == 403
