import pytest
import pyotp

def test_get_qr_code_student_role(client, student_auth_headers, student_user):
    response = client.get('/api/qr/me/code', headers=student_auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'code' in data
    assert 'expires_in' in data
    assert len(data['code']) == 6

def test_get_qr_code_unauthorized_role(client, director_auth_headers):
    response = client.get('/api/qr/me/code', headers=director_auth_headers)
    assert response.status_code == 403

def test_verify_qr_valid(client, teacher_auth_headers, student_user, student_secret):
    totp = pyotp.TOTP(student_secret, interval=20)
    code = totp.now()
    
    payload = {
        "student_id": student_user.id,
        "code": code
    }
    response = client.post('/api/qr/verify', json=payload, headers=teacher_auth_headers)
    assert response.status_code == 200
    assert response.get_json()['valid'] is True

def test_verify_qr_invalid_code(client, teacher_auth_headers, student_user):
    payload = {
        "student_id": student_user.id,
        "code": "000000"
    }
    response = client.post('/api/qr/verify', json=payload, headers=teacher_auth_headers)
    assert response.status_code == 400
    assert response.get_json()['valid'] is False

def test_verify_qr_missing_fields(client, teacher_auth_headers):
    response = client.post('/api/qr/verify', json={}, headers=teacher_auth_headers)
    assert response.status_code == 400

def test_verify_qr_as_tutor_forbidden(client, tutor_auth_headers, student_user):
    payload = {"student_id": student_user.id, "code": "123456"}
    response = client.post('/api/qr/verify', json=payload, headers=tutor_auth_headers)
    assert response.status_code == 403

def test_verify_qr_as_student_forbidden(client, student_auth_headers, student_user):
    payload = {"student_id": student_user.id, "code": "123456"}
    response = client.post('/api/qr/verify', json=payload, headers=student_auth_headers)
    assert response.status_code == 403

def test_get_qr_info_as_director(client, director_auth_headers, student_user):
    response = client.get(f'/api/qr/student/{student_user.id}', headers=director_auth_headers)
    assert response.status_code == 200
    assert 'student_id' in response.get_json()

def test_get_qr_info_as_teacher(client, teacher_auth_headers, student_user):
    response = client.get(f'/api/qr/student/{student_user.id}', headers=teacher_auth_headers)
    assert response.status_code == 200

def test_get_qr_info_as_tutor_forbidden(client, tutor_auth_headers, student_user):
    response = client.get(f'/api/qr/student/{student_user.id}', headers=tutor_auth_headers)
    assert response.status_code == 403

def test_get_qr_info_not_found(client, director_auth_headers):
    response = client.get('/api/qr/student/999999', headers=director_auth_headers)
    assert response.status_code == 404