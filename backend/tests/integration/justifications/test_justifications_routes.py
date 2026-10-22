"""Justificaciones de ausencia: solicitud del tutor y revisión de la dirección."""
from datetime import date, timedelta

import pytest
from sqlalchemy import text

from app.core import clock
from app.extensions import db
from tests.conftest import auth_header


@pytest.fixture()
def tutor(client, login):
    return auth_header(login("tutor1"))


@pytest.fixture()
def director(client, login):
    return auth_header(login("directora.mquispe"))


def _limpiar_justificaciones_del_tutor() -> None:
    """Borra las justificaciones creadas por el tutor 1 (usuario 10).

    Primero suelta el enlace de las asistencias, porque la tabla 'asistencias'
    referencia a la justificación.
    """
    db.session.rollback()
    db.session.execute(
        text(
            "update sesco.asistencias set id_justificacion = null where id_justificacion in "
            "(select j.id_justificacion from sesco.justificaciones_ausencia j "
            " join sesco.tutores t on j.id_tutor = t.id_tutor where t.id_usuario = :u)"
        ),
        {"u": 10},
    )
    db.session.execute(
        text(
            "delete from sesco.justificaciones_ausencia j using sesco.tutores t "
            "where j.id_tutor = t.id_tutor and t.id_usuario = :u"
        ),
        {"u": 10},
    )
    db.session.commit()


def test_el_tutor_solicita_una_justificacion(client, tutor):
    _limpiar_justificaciones_del_tutor()
    hoy = clock.now().date()
    respuesta = client.post(
        "/api/justifications",
        json={
            "id_estudiante": 1,
            "fecha_inicio": hoy.isoformat(),
            "fecha_fin": hoy.isoformat(),
            "motivo": "Consulta médica en el centro de salud.",
        },
        headers=tutor,
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.get_json()
    assert cuerpo["estado"] == "pendiente"
    assert cuerpo["id_estudiante"] == 1
    assert cuerpo["motivo"] == "Consulta médica en el centro de salud."


def test_el_tutor_no_crea_justificaciones_para_otros_tutores(client, tutor):
    """El id_tutor sale de la sesión: no se puede suplantar a otro tutor."""
    _limpiar_justificaciones_del_tutor()
    hoy = clock.now().date()
    respuesta = client.post(
        "/api/justifications",
        json={
            "id_estudiante": 1,
            "id_tutor": 2,
            "fecha_inicio": hoy.isoformat(),
            "fecha_fin": hoy.isoformat(),
            "motivo": "Intento de suplantar al tutor.",
        },
        headers=tutor,
    )
    assert respuesta.status_code == 201
    assert respuesta.get_json()["id_tutor"] != 2


def test_fechas_invertidas_se_rechazan(client, tutor):
    hoy = clock.now().date()
    respuesta = client.post(
        "/api/justifications",
        json={
            "id_estudiante": 1,
            "fecha_inicio": hoy.isoformat(),
            "fecha_fin": (hoy - timedelta(days=3)).isoformat(),
            "motivo": "Rango imposible.",
        },
        headers=tutor,
    )
    assert respuesta.status_code == 422
    assert respuesta.get_json()["error"]["codigo"] == "datos_invalidos"


def test_sin_datos_obligatorios_se_rechaza(client, tutor):
    respuesta = client.post("/api/justifications", json={}, headers=tutor)
    assert respuesta.status_code == 422


def test_el_profesor_no_solicita_justificaciones(client, login):
    respuesta = client.post(
        "/api/justifications",
        json={
            "id_estudiante": 1,
            "fecha_inicio": "2026-03-02",
            "fecha_fin": "2026-03-02",
            "motivo": "Prueba",
        },
        headers=auth_header(login("prof.cmamani")),
    )
    assert respuesta.status_code == 403


def test_la_direccion_revisa_y_justifica_la_asistencia(client, tutor, director):
    _limpiar_justificaciones_del_tutor()
    hoy = clock.now().date()
    creada = client.post(
        "/api/justifications",
        json={
            "id_estudiante": 1,
            "fecha_inicio": hoy.isoformat(),
            "fecha_fin": hoy.isoformat(),
            "motivo": "Enfermedad del estudiante.",
        },
        headers=tutor,
    ).get_json()

    revisada = client.put(
        f"/api/justifications/{creada['id_justificacion']}/estado",
        json={"estado": "justificada", "comentario": "Se acepta el justificante."},
        headers=director,
    )
    assert revisada.status_code == 200
    cuerpo = revisada.get_json()
    assert cuerpo["estado"] == "justificada"
    assert cuerpo["revisada_por"] is not None
    assert cuerpo["revisada_en"] is not None
    assert cuerpo["comentario_revision"] == "Se acepta el justificante."


def test_un_tutor_no_revisa_justificaciones(client, tutor):
    _limpiar_justificaciones_del_tutor()
    hoy = clock.now().date()
    creada = client.post(
        "/api/justifications",
        json={
            "id_estudiante": 1,
            "fecha_inicio": hoy.isoformat(),
            "fecha_fin": hoy.isoformat(),
            "motivo": "Prueba de permiso.",
        },
        headers=tutor,
    ).get_json()
    respuesta = client.put(
        f"/api/justifications/{creada['id_justificacion']}/estado",
        json={"estado": "justificada"},
        headers=tutor,
    )
    assert respuesta.status_code == 403


def test_el_tutor_solo_ve_las_suyas(client, tutor):
    _limpiar_justificaciones_del_tutor()
    hoy = clock.now().date()
    creada = client.post(
        "/api/justifications",
        json={
            "id_estudiante": 1,
            "fecha_inicio": hoy.isoformat(),
            "fecha_fin": hoy.isoformat(),
            "motivo": "Solo visible para su tutor.",
        },
        headers=tutor,
    ).get_json()
    listado = client.get("/api/justifications", headers=tutor).get_json()
    assert creada["id_justificacion"] in {j["id_justificacion"] for j in listado["items"]}
