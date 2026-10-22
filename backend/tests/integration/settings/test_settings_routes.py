"""Configuración de la asistencia: se lee y se guarda en la base de datos."""


def test_sin_sesion_no_puede_leer(client):
    response = client.get("/api/settings/attendance")
    assert response.status_code == 401


def test_leer_la_configuracion(client, director_auth_headers):
    response = client.get("/api/settings/attendance", headers=director_auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "tolerancia_ingreso_min" in data
    assert "limite_tardanza_min" in data
    assert data["tolerancia_ingreso_min"] >= 0


def test_la_configuracion_se_guarda_en_la_base(client, director_auth_headers):
    anterior = client.get("/api/settings/attendance", headers=director_auth_headers).get_json()
    response = client.put(
        "/api/settings/attendance",
        json={"tolerancia_ingreso_min": 12, "limite_tardanza_min": 40},
        headers=director_auth_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["tolerancia_ingreso_min"] == 12
    assert response.get_json()["limite_tardanza_min"] == 40

    # Y sigue guardada al releerla.
    assert client.get("/api/settings/attendance", headers=director_auth_headers).get_json()["tolerancia_ingreso_min"] == 12

    client.put(
        "/api/settings/attendance",
        json={
            "tolerancia_ingreso_min": anterior["tolerancia_ingreso_min"],
            "limite_tardanza_min": anterior["limite_tardanza_min"],
        },
        headers=director_auth_headers,
    )


def test_valores_fuera_de_rango(client, director_auth_headers):
    response = client.put(
        "/api/settings/attendance",
        json={"tolerancia_ingreso_min": -5, "limite_tardanza_min": 10},
        headers=director_auth_headers,
    )
    assert response.status_code == 422


def test_un_docente_no_cambia_la_configuracion(client, teacher_auth_headers):
    response = client.put(
        "/api/settings/attendance",
        json={"tolerancia_ingreso_min": 10, "limite_tardanza_min": 30},
        headers=teacher_auth_headers,
    )
    assert response.status_code == 403


def test_un_tutor_no_cambia_la_configuracion(client, tutor_auth_headers):
    response = client.put(
        "/api/settings/attendance",
        json={"tolerancia_ingreso_min": 10, "limite_tardanza_min": 30},
        headers=tutor_auth_headers,
    )
    assert response.status_code == 403
