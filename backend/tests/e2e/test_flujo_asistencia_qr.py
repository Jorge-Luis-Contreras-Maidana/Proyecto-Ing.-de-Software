"""Flujo completo: un estudiante se acredita, el docente lo escanea y se registra.

Recorre la cadena real de la aplicación: login del estudiante, lectura de su
credencial QR, login del docente, escaneo del código, verificación del registro
y consulta del historial. Es el camino que se ejecuta en un aula.
"""
from sqlalchemy import text

from app.core import clock
from app.extensions import db


def _limpiar_de_hoy(id_estudiante: int) -> None:
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


def test_flujo_acredentar_esc_anear_y_registrar(client, login, qr_code):
    _limpiar_de_hoy(1)

    # 1. El estudiante entra y ve su credencial.
    sesion_estudiante = client.post(
        "/api/auth/login", json={"nombre_usuario": "estudiante1", "contrasena": "Demo1234!"}
    )
    assert sesion_estudiante.status_code == 200
    token_estudiante = sesion_estudiante.get_json()["access_token"]
    credencial = client.get(
        "/api/qr/me/code", headers={"Authorization": f"Bearer {token_estudiante}"}
    )
    assert credencial.status_code == 200
    datos_credencial = credencial.get_json()
    assert datos_credencial["id_estudiante"] == 1
    assert datos_credencial["imagen"].startswith("data:image/png;base64,")

    # 2. El docente entra y consulta las clases de hoy.
    sesion_docente = client.post(
        "/api/auth/login", json={"nombre_usuario": "prof.cmamani", "contrasena": "Demo1234!"}
    )
    token_docente = sesion_docente.get_json()["access_token"]
    cabeceras = {"Authorization": f"Bearer {token_docente}"}
    clases = client.get("/api/attendance/hoy", headers=cabeceras)
    assert clases.status_code == 200
    items = clases.get_json()["items"]
    assert len(items) > 0

    # 3. El docente escanea el QR del estudiante.
    registro = client.post(
        "/api/attendance/registrar",
        json={"id_estudiante": 1, "codigo": datos_credencial["codigo"]},
        headers=cabeceras,
    )
    assert registro.status_code in (200, 201)
    cuerpo = registro.get_json()
    assert cuerpo["id_estudiante"] == 1
    assert cuerpo["estado"] in ("presente", "tarde", "ausente")
    assert cuerpo["hora_ingreso"] is not None

    # 4. La asistencia aparece en el detalle de la clase.
    detalle = client.get(f"/api/attendance/sesion/{cuerpo['id_sesion_clase']}", headers=cabeceras)
    assert detalle.status_code == 200
    estudiante = next(
        e for e in detalle.get_json()["estudiantes"] if e["id_estudiante"] == 1
    )
    assert estudiante["estado"] == cuerpo["estado"]
    assert estudiante["hora_ingreso"] is not None
    assert estudiante["metodo_ingreso"] == "qr"

    # 5. Y en el historial del estudiante.
    historial = client.get("/api/attendance/estudiante/1", headers=cabeceras)
    assert historial.status_code == 200
    assert any(i["id_asistencia"] == cuerpo["id_asistencia"] for i in historial.get_json()["items"])


def test_el_tutor_ve_la_asistencia_de_su_estudiante(client, login):
    """El tutor solo ve a los estudiantes vinculados a él."""
    cabecera = {"Authorization": f"Bearer {login('tutor1').get_json()['access_token']}"}
    historial = client.get("/api/attendance/estudiante/1", headers=cabecera)
    assert historial.status_code == 200

    ajeno = client.get("/api/attendance/estudiante/2", headers=cabecera)
    assert ajeno.status_code == 404
