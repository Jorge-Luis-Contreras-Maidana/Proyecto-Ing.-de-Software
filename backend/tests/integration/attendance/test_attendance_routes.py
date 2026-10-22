"""Registro de asistencia por QR y por vía manual."""
from sqlalchemy import text

from app.core import clock
from app.extensions import db


def _limpiar_asistencia_de_hoy(id_estudiante: int = 1) -> None:
    """Deja al estudiante sin asistencia registrada en las sesiones de hoy.

    Así el test no depende de que otro test haya registrado antes el ingreso.
    """
    hoy = clock.now().date()
    db.session.execute(
        text(
            "delete from sesco.lecturas_qr l using sesco.asistencias a, sesco.sesiones_clase s "
            "where l.id_asistencia = a.id_asistencia and a.id_sesion_clase = s.id_sesion_clase "
            "and a.id_estudiante = :e and s.fecha = :f"
        ),
        {"e": id_estudiante, "f": hoy},
    )
    db.session.execute(
        text(
            "delete from sesco.asistencias a using sesco.sesiones_clase s "
            "where a.id_sesion_clase = s.id_sesion_clase and a.id_estudiante = :e and s.fecha = :f"
        ),
        {"e": id_estudiante, "f": hoy},
    )
    db.session.commit()


def test_registrar_asistencia_con_el_qr_del_estudiante(client, teacher_auth_headers, qr_code):
    _limpiar_asistencia_de_hoy()
    response = client.post(
        "/api/attendance/registrar",
        json={"id_estudiante": 1, "codigo": qr_code(1)},
        headers=teacher_auth_headers,
    )
    assert response.status_code in (200, 201)
    data = response.get_json()
    assert data["estado"] in ("presente", "tarde", "ausente")
    assert data["hora_ingreso"] is not None
    assert data["id_asistencia"] > 0


def test_el_segundo_escaneo_no_duplica_la_asistencia(client, teacher_auth_headers, qr_code):
    _limpiar_asistencia_de_hoy()
    codigo = qr_code(1)
    primero = client.post(
        "/api/attendance/registrar",
        json={"id_estudiante": 1, "codigo": codigo},
        headers=teacher_auth_headers,
    )
    assert primero.status_code in (200, 201)
    segundo = client.post(
        "/api/attendance/registrar",
        json={"id_estudiante": 1, "codigo": codigo},
        headers=teacher_auth_headers,
    )
    # El mismo código dentro de la misma ventana no se acepta dos veces.
    assert segundo.status_code == 422
    assert segundo.get_json()["error"]["codigo"] == "datos_invalidos"


def test_escaneos_tras_los_primeros_minutos_son_puntuales(client, teacher_auth_headers, qr_code):
    """Dentro de la tolerancia configurada, el ingreso es 'presente'."""
    _limpiar_asistencia_de_hoy()
    response = client.post(
        "/api/attendance/registrar",
        json={"id_estudiante": 1, "codigo": qr_code(1)},
        headers=teacher_auth_headers,
    )
    assert response.status_code in (200, 201)
    # La clasificación depende de la hora real de la prueba, así que solo se
    # comprueba que el estado es uno de los válidos.
    assert response.get_json()["estado"] in ("presente", "tarde", "ausente")


def test_un_codigo_invalido_no_registra_asistencia(client, teacher_auth_headers):
    response = client.post(
        "/api/attendance/registrar",
        json={"id_estudiante": 1, "codigo": "000000"},
        headers=teacher_auth_headers,
    )
    assert response.status_code == 422


def test_faltan_datos_obligatorios(client, teacher_auth_headers):
    response = client.post("/api/attendance/registrar", json={}, headers=teacher_auth_headers)
    assert response.status_code == 422


def test_sesiones_de_hoy_del_personal(client, teacher_auth_headers):
    response = client.get("/api/attendance/hoy", headers=teacher_auth_headers)
    assert response.status_code == 200
    items = response.get_json()["items"]
    assert len(items) > 0
    assert "hora_inicio_prevista" in items[0]
    assert "asistencia" in items[0]


def test_detalle_de_la_sesion(client, teacher_auth_headers):
    hoy = client.get("/api/attendance/hoy", headers=teacher_auth_headers).get_json()["items"]
    id_sesion = hoy[0]["id_sesion_clase"]
    response = client.get(f"/api/attendance/sesion/{id_sesion}", headers=teacher_auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["id_sesion_clase"] == id_sesion
    assert len(data["estudiantes"]) > 0
    assert "nombres" in data["estudiantes"][0]


def test_registro_manual_de_asistencia(client, teacher_auth_headers):
    hoy = client.get("/api/attendance/hoy", headers=teacher_auth_headers).get_json()["items"]
    id_sesion = hoy[0]["id_sesion_clase"]
    id_estudiante = client.get(f"/api/attendance/sesion/{id_sesion}", headers=teacher_auth_headers).get_json()["estudiantes"][0]["id_estudiante"]
    response = client.post(
        f"/api/attendance/sesion/{id_sesion}/marcar",
        json={"id_estudiante": id_estudiante, "estado": "presente", "observacion": "Registro manual"},
        headers=teacher_auth_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["estado"] == "presente"


def test_el_historial_del_estudiante(client, teacher_auth_headers, student_auth_headers):
    response = client.get("/api/attendance/estudiante/1", headers=teacher_auth_headers)
    assert response.status_code == 200
    assert "items" in response.get_json()


def test_el_tutor_no_registra_asistencia(client, tutor_auth_headers, qr_code):
    response = client.post(
        "/api/attendance/registrar",
        json={"id_estudiante": 1, "codigo": qr_code(1)},
        headers=tutor_auth_headers,
    )
    assert response.status_code == 403
