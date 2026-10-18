import pytest
from sqlalchemy import text

from app import create_app
from app.core.security.hashing import hash_password
from app.extensions import db
from app.modules.auth import auth_required

PASSWORD = "Demo1234!"
USUARIOS_DE_PRUEBA = (
    "directora.mquispe",
    "prof.cmamani",
    "prof.rchoque",
    "tutor1",
    "tutor2",
    "estudiante1",
)

_TEST = "SELECT id_estudiante FROM sesco.estudiantes WHERE codigo_estudiante LIKE 'TEST-%'"


def _limpiar_datos_de_prueba():
    """Borra registros de prueba y resetea la secuencia de sesiones_usuario."""
    db.session.rollback()
    sql_statements = [
        "DELETE FROM sesco.sesiones_usuario WHERE id_sesion > 4",
        f"DELETE FROM sesco.observaciones_estudiante WHERE id_estudiante IN ({_TEST})",
        f"DELETE FROM sesco.estudiante_tutor WHERE id_estudiante IN ({_TEST})",
        f"DELETE FROM sesco.inscripciones WHERE id_estudiante IN ({_TEST})",
        "DELETE FROM sesco.estudiantes WHERE codigo_estudiante LIKE 'TEST-%'",
        "SELECT setval(pg_get_serial_sequence('sesco.sesiones_usuario', 'id_sesion'), COALESCE((SELECT MAX(id_sesion) FROM sesco.sesiones_usuario), 1))",
    ]
    for sql in sql_statements:
        try:
            db.session.execute(text(sql))
            db.session.commit()
        except Exception:
            db.session.rollback()


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    app.add_url_rule(
        "/_test/solo-director",
        endpoint="solo_director",
        view_func=auth_required("director")(lambda: {"ok": True}),
    )
    with app.app_context():
        try:
            db.session.execute(
                text("UPDATE sesco.usuarios SET hash_contrasena = :h WHERE nombre_usuario = ANY(:u)"),
                {"h": hash_password(PASSWORD), "u": list(USUARIOS_DE_PRUEBA)},
            )
            db.session.commit()
        except Exception:
            db.session.rollback()

        _limpiar_datos_de_prueba()
        yield app
        _limpiar_datos_de_prueba()


@pytest.fixture(autouse=True)
def cleanup_db_session(app):
    """Garantiza la limpieza de transacciones de BD antes y después de cada test."""
    with app.app_context():
        db.session.rollback()
        db.session.remove()
    yield
    with app.app_context():
        db.session.rollback()
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login(client):
    def _login(usuario="directora.mquispe", contrasena=PASSWORD):
        return client.post("/api/auth/login", json={"nombre_usuario": usuario, "contrasena": contrasena})

    return _login


def auth_header(response):
    data = response.get_json() or {}
    token = data.get("access_token") or data.get("token") or ""
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def director(login):
    return auth_header(login("directora.mquispe", PASSWORD))


@pytest.fixture()
def director_auth_headers(director):
    return director


@pytest.fixture()
def teacher_auth_headers(login):
    return auth_header(login("prof.cmamani", PASSWORD))


@pytest.fixture()
def tutor_auth_headers(login):
    return auth_header(login("tutor1", PASSWORD))


@pytest.fixture()
def student_auth_headers(login):
    return auth_header(login("estudiante1", PASSWORD))


class DummyStudent:
    def __init__(self, student_id: int):
        self.id = student_id


@pytest.fixture()
def student_user():
    return DummyStudent(1)


@pytest.fixture()
def student_secret():
    return "JBSWY3DPEHPK3PXP"