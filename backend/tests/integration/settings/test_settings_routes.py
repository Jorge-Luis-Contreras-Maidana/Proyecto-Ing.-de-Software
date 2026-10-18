import pytest

def test_get_settings_unauthorized(client):
    response = client.get('/api/settings/attendance')
    assert response.status_code == 401

def test_get_settings_authorized(client, director_auth_headers):
    response = client.get('/api/settings/attendance', headers=director_auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'tolerance_minutes' in data
    assert 'absence_limit_minutes' in data

def test_update_settings_as_director(client, director_auth_headers):
    payload = {
        "tolerance_minutes": 15,
        "absence_limit_minutes": 45
    }
    response = client.put('/api/settings/attendance', json=payload, headers=director_auth_headers)
    assert response.status_code == 200
    assert response.get_json()['tolerance_minutes'] == 15

def test_update_settings_invalid_values(client, director_auth_headers):
    payload = {
        "tolerance_minutes": -5,
        "absence_limit_minutes": 10
    }
    response = client.put('/api/settings/attendance', json=payload, headers=director_auth_headers)
    assert response.status_code == 400

def test_update_settings_as_teacher_forbidden(client, teacher_auth_headers):
    payload = {"tolerance_minutes": 10, "absence_limit_minutes": 30}
    response = client.put('/api/settings/attendance', json=payload, headers=teacher_auth_headers)
    assert response.status_code == 403

def test_update_settings_as_tutor_forbidden(client, tutor_auth_headers):
    payload = {"tolerance_minutes": 10, "absence_limit_minutes": 30}
    response = client.put('/api/settings/attendance', json=payload, headers=tutor_auth_headers)
    assert response.status_code == 403