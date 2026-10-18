import pytest
import pyotp

def test_registrar_asistencia_exitoso(client, teacher_auth_headers, student_secret):
    totp = pyotp.TOTP(student_secret, interval=20)
    code = totp.now()

    payload = {"student_id": 1, "code": code}
    response = client.post("/api/attendance/registrar", json=payload, headers=teacher_auth_headers)
    assert response.status_code in (200, 201)
    assert "estado" in response.get_json()

def test_registrar_asistencia_duplicada_idempotente(client, teacher_auth_headers, student_secret):
    totp = pyotp.TOTP(student_secret, interval=20)
    code = totp.now()

    payload = {"student_id": 1, "code": code}
    client.post("/api/attendance/registrar", json=payload, headers=teacher_auth_headers)
    
    # Segundo intento
    response = client.post("/api/attendance/registrar", json=payload, headers=teacher_auth_headers)
    assert response.status_code == 200
    assert "ya registrado" in response.get_json()["mensaje"]

def test_registrar_asistencia_qr_invalido(client, teacher_auth_headers):
    payload = {"student_id": 1, "code": "000000"}
    response = client.post("/api/attendance/registrar", json=payload, headers=teacher_auth_headers)
    assert response.status_code == 400