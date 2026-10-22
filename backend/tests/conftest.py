import pytest
from sqlalchemy import select, text

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
    "estudiante2",
    "estudiante3",
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


# ---------- credenciales QR ----------
MARCADOR_CREDENCIAL = "DEMO_SECRETO_CIFRADO_"


def codigo_qr_de(id_estudiante: int) -> str:
    """Código TOTP vigente del estudiante, tal como lo vería su pantalla.

    Si la credencial guardada es un marcador de demostración (no se puede
    descifrar), emite una nueva para que el test no dependa de un paso previo.
    """
    from app.core import clock
    from app.core.security.totp_crypto import descifrar
    from app.modules.qr.models.qr import CredencialQR
    from app.modules.qr.services.qr_service import QRService
    from app.modules.qr.services.totp_service import TOTPService

    credencial = db.session.execute(
        select(CredencialQR).where(
            CredencialQR.id_estudiante == id_estudiante,
            CredencialQR.estado == "activa",
        )
    ).scalars().first()
    if credencial is None or credencial.secreto_totp_cifrado.startswith(MARCADOR_CREDENCIAL):
        if credencial is not None:
            credencial.estado = "revocada"
            credencial.revocada_en = clock.now()
            db.session.commit()
        credencial = QRService().emitir_si_falta(id_estudiante)
    return TOTPService.get_current_code_and_ttl(descifrar(credencial.secreto_totp_cifrado))[0]


@pytest.fixture()
def qr_code():
    """Devuelve el código QR vigente de un estudiante: qr_code(1)."""
    return codigo_qr_de


def limpiar_lecturas_qr(id_estudiante: int) -> None:
    """Borra las lecturas de QR de un estudiante.

    El mismo código no puede aceptarse dos veces dentro de una ventana, así
    que los tests que verifican un código necesitan partir de cero.
    """
    db.session.execute(
        text(
            "delete from sesco.lecturas_qr l using sesco.credenciales_qr c "
            "where l.id_credencial = c.id_credencial and c.id_estudiante = :e"
        ),
        {"e": id_estudiante},
    )
    db.session.commit()


@pytest.fixture(scope="session", autouse=True)
def horario_de_hoy(app):
    """Garantiza que exista el horario de clases de hoy en la base de pruebas."""
    from app.modules.attendance.services.schedule_service import ScheduleService

    with app.app_context():
        ScheduleService().asegurar_hoy()
        yield
