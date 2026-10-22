"""Avisos institucionales: publicación, destinatarios y lectura."""
import pytest
from sqlalchemy import text

from app.extensions import db
from tests.conftest import auth_header


@pytest.fixture()
def director(client, login):
    return auth_header(login("directora.mquispe"))


@pytest.fixture()
def profesor(client, login):
    return auth_header(login("prof.cmamani"))


@pytest.fixture()
def tutor(client, login):
    return auth_header(login("tutor1"))


def _limpiar_avisos_de_prueba() -> None:
    db.session.rollback()
    db.session.execute(
        text("delete from sesco.lecturas_avisos where id_aviso in (select id_aviso from sesco.avisos where titulo like 'PRUEBA-%')")
    )
    db.session.execute(
        text("delete from sesco.avisos_destinatarios_roles where id_aviso in (select id_aviso from sesco.avisos where titulo like 'PRUEBA-%')")
    )
    db.session.execute(text("delete from sesco.avisos where titulo like 'PRUEBA-%'"))
    db.session.commit()


def test_el_director_publica_un_aviso(client, director):
    _limpiar_avisos_de_prueba()
    respuesta = client.post(
        "/api/announcements",
        json={
            "titulo": "PRUEBA-Inicio de gestión",
            "contenido": "Serecallan las fechas.",
            "importante": True,
            "estado": "publicado",
            "roles_destinatarios": ["tutor", "estudiante"],
        },
        headers=director,
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.get_json()
    assert cuerpo["titulo"] == "PRUEBA-Inicio de gestión"
    assert cuerpo["importante"] is True
    assert cuerpo["estado"] == "publicado"
    assert set(cuerpo["roles_destinatarios"]) == {"tutor", "estudiante"}
    assert cuerpo["publicado_en"] is not None


def test_el_aviso_aparece_para_los_roles_destinatarios(client, director, tutor):
    _limpiar_avisos_de_prueba()
    creado = client.post(
        "/api/announcements",
        json={
            "titulo": "PRUEBA-Solo tutores",
            "contenido": "Contenido del aviso.",
            "estado": "publicado",
            "roles_destinatarios": ["tutor"],
        },
        headers=director,
    ).get_json()

    listado = client.get("/api/announcements", headers=tutor).get_json()
    assert creado["id_aviso"] in {a["id_aviso"] for a in listado["items"]}


def test_el_aviso_no_aparece_para_otros_roles(client, director, profesor):
    _limpiar_avisos_de_prueba()
    creado = client.post(
        "/api/announcements",
        json={
            "titulo": "PRUEBA-Solo tutores otra vez",
            "contenido": "Contenido del aviso.",
            "estado": "publicado",
            "roles_destinatarios": ["tutor"],
        },
        headers=director,
    ).get_json()

    listado = client.get("/api/announcements", headers=profesor).get_json()
    assert creado["id_aviso"] not in {a["id_aviso"] for a in listado["items"]}


def test_el_usuario_marca_el_aviso_como_leido(client, director, tutor):
    _limpiar_avisos_de_prueba()
    creado = client.post(
        "/api/announcements",
        json={
            "titulo": "PRUEBA-Para leer",
            "contenido": "Contenido del aviso.",
            "estado": "publicado",
            "roles_destinatarios": ["tutor"],
        },
        headers=director,
    ).get_json()

    leido = client.put(f"/api/announcements/{creado['id_aviso']}/leer", headers=tutor)
    assert leido.status_code == 200
    assert leido.get_json()["leido"] is True


def test_un_docente_no_publica_avisos(client, profesor):
    respuesta = client.post(
        "/api/announcements",
        json={"titulo": "PRUEBA-No permitido", "contenido": "x"},
        headers=profesor,
    )
    assert respuesta.status_code == 403


def test_sin_titulo_se_rechaza(client, director):
    respuesta = client.post("/api/announcements", json={"contenido": "Sin título"}, headers=director)
    assert respuesta.status_code == 422


def test_los_avisos_de_inasistencia_docente(client, director):
    respuesta = client.get("/api/announcements/inasistencia-docente", headers=director)
    assert respuesta.status_code == 200
    assert "items" in respuesta.get_json()
