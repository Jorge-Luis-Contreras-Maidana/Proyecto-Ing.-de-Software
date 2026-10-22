"""Bitácora de auditoría: solo la dirección puede consultarla."""
import pytest
from sqlalchemy import text

from app.extensions import db
from tests.conftest import auth_header


@pytest.fixture()
def director(client, login):
    return auth_header(login("directora.mquispe"))


def _limpiar_auditoria_de_prueba() -> None:
    db.session.rollback()
    db.session.execute(text("delete from sesco.bitacora_auditoria where detalle like 'PRUEBA-%'"))
    db.session.commit()


def test_la_direccion_consulta_la_bitacora(client, director):
    respuesta = client.get("/api/audit", headers=director)
    assert respuesta.status_code == 200
    cuerpo = respuesta.get_json()
    assert "items" in cuerpo and "total" in cuerpo


def test_se_puede_filtrar_por_operacion(client, director):
    respuesta = client.get("/api/audit?operacion=CONSULTAR", headers=director)
    assert respuesta.status_code == 200
    for evento in respuesta.get_json()["items"]:
        assert evento["operacion"] == "CONSULTAR"


def test_se_puede_filtrar_por_entidad(client, director):
    respuesta = client.get("/api/audit?entidad=estudiantes", headers=director)
    assert respuesta.status_code == 200
    for evento in respuesta.get_json()["items"]:
        assert evento["entidad"] == "estudiantes"


def test_la_paginacion_funciona(client, director):
    respuesta = client.get("/api/audit?page=1&per_page=2", headers=director)
    assert respuesta.status_code == 200
    cuerpo = respuesta.get_json()
    assert len(cuerpo["items"]) <= 2


def test_un_docente_no_consulta_la_bitacora(client, login):
    headers = auth_header(login("prof.cmamani"))
    assert client.get("/api/audit", headers=headers).status_code == 403


def test_un_tutor_no_consulta_la_bitacora(client, login):
    headers = auth_header(login("tutor1"))
    assert client.get("/api/audit", headers=headers).status_code == 403


def test_un_evento_existente_se_consulta(client, director):
    listado = client.get("/api/audit", headers=director).get_json()["items"]
    if not listado:
        pytest.skip("No hay eventos de auditoría en la base de pruebas.")
    id_evento = listado[0]["id_evento"]
    respuesta = client.get(f"/api/audit/{id_evento}", headers=director)
    assert respuesta.status_code == 200
    assert respuesta.get_json()["id_evento"] == id_evento
