import uuid

import pytest

from tests.conftest import auth_header


@pytest.fixture()
def director(login):
    return auth_header(login("directora.mquispe"))


def nuevo(client, headers, **extra):
    datos = {
        "codigo_estudiante": f"TEST-{uuid.uuid4().hex[:8]}",
        "nombres": "Ana",
        "apellidos": "Prueba",
        "fecha_nacimiento": "2014-05-10",
        "genero": "femenino",
        "id_curso": 1,
    }
    datos.update(extra)
    return client.post("/api/students", json=datos, headers=headers)


def ids(response):
    return {e["id_estudiante"] for e in response.get_json()["items"]}


# ---------- registrar, modificar, consultar y dar de baja (RF-02.1) ----------
def test_el_director_registra_un_estudiante_con_su_curso(client, director):
    r = nuevo(client, director)
    assert r.status_code == 201
    body = r.get_json()
    assert body["estado"] == "activo" and body["curso"]["id_curso"] == 1
    detalle = client.get(f"/api/students/{body['id_estudiante']}", headers=director)
    assert detalle.status_code == 200 and detalle.get_json()["tutores"] == []


def test_codigo_duplicado_se_rechaza(client, director):
    codigo = f"TEST-{uuid.uuid4().hex[:8]}"
    assert nuevo(client, director, codigo_estudiante=codigo).status_code == 201
    r = nuevo(client, director, codigo_estudiante=codigo)
    assert r.status_code == 409 and r.get_json()["error"]["codigo"] == "registro_duplicado"


def test_validaciones_al_registrar(client, director):
    assert nuevo(client, director, fecha_nacimiento="2999-01-01").status_code == 422
    assert nuevo(client, director, id_curso=9999).status_code == 404
    r = client.post("/api/students", json={"nombres": "Solo nombre"}, headers=director)
    assert r.status_code == 422 and r.get_json()["error"]["codigo"] == "datos_invalidos"


def test_modificar_datos_y_curso(client, director):
    sid = nuevo(client, director).get_json()["id_estudiante"]
    r = client.put(f"/api/students/{sid}", json={"nombres": "Lucía", "id_curso": 2}, headers=director)
    assert r.status_code == 200
    assert r.get_json()["nombres"] == "Lucía" and r.get_json()["curso"]["id_curso"] == 2


def test_dar_de_baja_no_borra_al_estudiante(client, director):
    creado = nuevo(client, director).get_json()
    sid, codigo = creado["id_estudiante"], creado["codigo_estudiante"]
    assert client.delete(f"/api/students/{sid}", headers=director).status_code == 200
    activos = client.get(f"/api/students?q={codigo}", headers=director).get_json()
    assert activos["total"] == 0
    retirados = client.get(f"/api/students?q={codigo}&estado=retirado", headers=director).get_json()
    assert retirados["total"] == 1  # el historial se conserva (RNF-06.1)
    assert client.put(f"/api/students/{sid}", json={"nombres": "X"}, headers=director).status_code == 422
    assert client.delete(f"/api/students/{sid}", headers=director).status_code == 422


def test_lista_con_busqueda_y_paginacion(client, director):
    creado = nuevo(client, director, nombres="Zoraida", apellidos="Quillahuaman").get_json()
    por_codigo = client.get(f"/api/students?q={creado['codigo_estudiante']}", headers=director).get_json()
    assert por_codigo["total"] == 1
    assert client.get("/api/students?q=quillahuaman", headers=director).get_json()["total"] >= 1
    pagina = client.get("/api/students?per_page=5&page=2", headers=director).get_json()
    assert len(pagina["items"]) == 5 and pagina["total"] >= 32
    assert client.get("/api/students?per_page=500", headers=director).status_code == 422


# ---------- quién puede qué (RF-01.3, RD-02.1) ----------
def test_profesor_y_tutor_no_pueden_registrar(client, login):
    for usuario in ("prof.cmamani", "tutor1"):
        r = nuevo(client, auth_header(login(usuario)))
        assert r.status_code == 403 and r.get_json()["error"]["codigo"] == "sin_permiso"


def test_el_profesor_solo_ve_estudiantes_de_sus_cursos(client, login):
    h = auth_header(login("prof.cmamani"))  # enseña solo en el curso 1
    r = client.get("/api/students?per_page=50", headers=h).get_json()
    assert r["total"] >= 8 and all(e["curso"]["id_curso"] == 1 for e in r["items"])
    assert client.get("/api/students/1", headers=h).status_code == 200
    assert client.get("/api/students/9", headers=h).status_code == 404  # de otro curso


def test_el_tutor_solo_ve_a_sus_hijos(client, login):
    h = auth_header(login("tutor1"))
    assert ids(client.get("/api/students", headers=h)) == {1, 31}
    hijo = client.get("/api/students/1", headers=h)
    assert hijo.status_code == 200 and hijo.get_json()["tutores"] == []
    ajeno = client.get("/api/students/2", headers=h)
    assert ajeno.status_code == 404 and ajeno.get_json()["error"]["codigo"] == "no_encontrado"


# ---------- observaciones (RF-02.2) ----------
def test_observaciones_con_acceso_restringido(client, login, director):
    sid = nuevo(client, director).get_json()["id_estudiante"]
    prof = auth_header(login("prof.cmamani"))
    otro_prof = auth_header(login("prof.rchoque"))
    tutor = auth_header(login("tutor1"))

    publica = client.post(f"/api/students/{sid}/observaciones", headers=prof,
                          json={"tipo": "asistencia", "descripcion": "Llega tarde los lunes."})
    assert publica.status_code == 201
    reservada = client.post(f"/api/students/{sid}/observaciones", headers=prof,
                            json={"tipo": "convivencia", "descripcion": "Situación reservada.", "confidencial": True})
    assert reservada.status_code == 201

    ver = lambda h: client.get(f"/api/students/{sid}/observaciones", headers=h)
    assert len(ver(director).get_json()["items"]) == 2   # el director ve todo
    assert len(ver(prof).get_json()["items"]) == 2       # el autor ve las suyas
    assert len(ver(otro_prof).get_json()["items"]) == 1  # otro profesor no ve la confidencial
    assert ver(tutor).status_code == 403                 # el tutor no accede a observaciones
    assert client.post("/api/students/9/observaciones", headers=prof,
                       json={"tipo": "otra", "descripcion": "x"}).status_code == 404


# ---------- vínculo con tutor confirmado por el director (RD-02.2) ----------
def test_el_vinculo_con_tutor_vale_solo_tras_la_confirmacion(client, login, director):
    sid = nuevo(client, director).get_json()["id_estudiante"]
    tutor2 = auth_header(login("tutor2"))

    r = client.post(f"/api/students/{sid}/tutores", headers=director,
                    json={"id_tutor": 2, "parentesco": "Madre", "es_contacto_principal": True})
    assert r.status_code == 201
    assert client.get(f"/api/students/{sid}", headers=tutor2).status_code == 404  # aún sin confirmar

    assert client.post(f"/api/students/{sid}/tutores/2/confirmar", headers=director).status_code == 200
    assert client.get(f"/api/students/{sid}", headers=tutor2).status_code == 200  # ya confirmado

    detalle = client.get(f"/api/students/{sid}", headers=director).get_json()
    assert detalle["tutores"][0]["id_tutor"] == 2 and detalle["tutores"][0]["confirmado"] is True
    assert detalle["tutores"][0]["nombre"]


def test_reglas_del_vinculo(client, director):
    sid = nuevo(client, director).get_json()["id_estudiante"]
    url = f"/api/students/{sid}/tutores"
    assert client.post(url, headers=director, json={"id_tutor": 2, "parentesco": "Madre", "es_contacto_principal": True}).status_code == 201
    assert client.post(url, headers=director, json={"id_tutor": 2, "parentesco": "Madre"}).status_code == 409   # repetido
    assert client.post(url, headers=director, json={"id_tutor": 3, "parentesco": "Tío", "es_contacto_principal": True}).status_code == 422  # ya hay principal
    assert client.post(url, headers=director, json={"id_tutor": 9999, "parentesco": "Tío"}).status_code == 404
    assert client.post(f"{url}/3/confirmar", headers=director).status_code == 404  # no vinculado