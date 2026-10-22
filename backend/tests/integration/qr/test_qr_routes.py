"""Credenciales QR: emisión por estudiante, validación y control de acceso."""

from tests.conftest import auth_header, limpiar_lecturas_qr


def test_el_estudiante_obtiene_su_propio_codigo(client, student_auth_headers):
    response = client.get("/api/qr/me/code", headers=student_auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["id_estudiante"] == 1
    assert len(data["codigo"]) == 6
    assert data["expira_en_segundos"] > 0
    assert data["imagen"].startswith("data:image/png;base64,")


def test_el_codigo_es_distinto_por_estudiante(client, teacher_auth_headers, qr_code):
    """El QR de un estudiante no sirve para otro (antes el secreto era uno solo)."""
    codigo = qr_code(1)
    response = client.post(
        "/api/qr/verify",
        json={"id_estudiante": 2, "codigo": codigo},
        headers=teacher_auth_headers,
    )
    assert response.status_code == 422
    assert response.get_json()["error"]["codigo"] == "datos_invalidos"


def test_un_docente_no_tiene_credencial_propia(client, director_auth_headers):
    response = client.get("/api/qr/me/code", headers=director_auth_headers)
    assert response.status_code == 404


def test_verificar_el_codigo_vigente(client, teacher_auth_headers, qr_code):
    limpiar_lecturas_qr(1)
    response = client.post(
        "/api/qr/verify",
        json={"id_estudiante": 1, "codigo": qr_code(1)},
        headers=teacher_auth_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["valido"] is True


def test_verificar_el_codigo_de_otro_estudiante_falla(client, teacher_auth_headers, qr_code):
    limpiar_lecturas_qr(2)
    response = client.post(
        "/api/qr/verify",
        json={"id_estudiante": 2, "codigo": qr_code(1)},
        headers=teacher_auth_headers,
    )
    assert response.status_code == 422


def test_verificar_un_codigo_invalido(client, teacher_auth_headers):
    response = client.post(
        "/api/qr/verify",
        json={"id_estudiante": 1, "codigo": "000000"},
        headers=teacher_auth_headers,
    )
    assert response.status_code == 422


def test_verificar_sin_datos(client, teacher_auth_headers):
    response = client.post("/api/qr/verify", json={}, headers=teacher_auth_headers)
    assert response.status_code == 422


def test_el_tutor_no_puede_verificar(client, tutor_auth_headers, qr_code):
    response = client.post(
        "/api/qr/verify",
        json={"id_estudiante": 1, "codigo": qr_code(1)},
        headers=tutor_auth_headers,
    )
    assert response.status_code == 403


def test_el_estudiante_no_puede_verificar(client, student_auth_headers, qr_code):
    response = client.post(
        "/api/qr/verify",
        json={"id_estudiante": 1, "codigo": qr_code(1)},
        headers=student_auth_headers,
    )
    assert response.status_code == 403


def test_informacion_del_estudiante_para_el_personal(client, director_auth_headers, teacher_auth_headers):
    for headers in (director_auth_headers, teacher_auth_headers):
        response = client.get("/api/qr/student/1", headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["id_estudiante"] == 1
        assert data["codigo_estudiante"] == "EST-0001"
        assert data["credencial_activa"] is True


def test_el_tutor_no_ve_la_credencial_de_otros(client, tutor_auth_headers):
    response = client.get("/api/qr/student/1", headers=tutor_auth_headers)
    assert response.status_code == 403


def test_estudiante_inexistente(client, director_auth_headers):
    response = client.get("/api/qr/student/999999", headers=director_auth_headers)
    assert response.status_code == 404
