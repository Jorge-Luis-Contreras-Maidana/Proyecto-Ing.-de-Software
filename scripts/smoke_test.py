"""Prueba de humo de todos los endpoints de SESCO.

Ejecuta una petición a cada ruta con los roles adecuados y comprueba que
responden. Es una comprobación rápida de que la aplicación está completa.

Uso (desde la carpeta backend, con el entorno virtual activado):
    python ../scripts/smoke_test.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

from app import create_app  # noqa: E402
from app.core import clock  # noqa: E402
from app.core.security.totp_crypto import descifrar  # noqa: E402
from app.extensions import db  # noqa: E402
from app.modules.qr.models.qr import CredencialQR  # noqa: E402
from app.modules.qr.services.totp_service import TOTPService  # noqa: E402
from sqlalchemy import select  # noqa: E402

ROLES = {
    "director": "directora.mquispe",
    "profesor": "prof.cmamani",
    "tutor": "tutor1",
    "estudiante": "estudiante1",
}

PRUEBAS = [
    ("GET", "/api/health", None, 200),
    ("POST", "/api/auth/login", "login", 200),
    ("GET", "/api/auth/me", "director", 200),
    ("GET", "/api/students", "director", 200),
    ("GET", "/api/students?q=sofia", "director", 200),
    ("GET", "/api/students/1", "director", 200),
    ("GET", "/api/students/1/observaciones", "director", 200),
    ("GET", "/api/qr/me/code", "estudiante", 200),
    ("GET", "/api/qr/student/1", "director", 200),
    ("GET", "/api/attendance/hoy", "profesor", 200),
    ("GET", "/api/settings/attendance", "director", 200),
    ("GET", "/api/justifications", "director", 200),
    ("GET", "/api/notifications", "director", 200),
    ("GET", "/api/notifications/no-leidas", "director", 200),
    ("GET", "/api/announcements", "director", 200),
    ("GET", "/api/announcements/inasistencia-docente", "director", 200),
    ("GET", "/api/followup/alertas", "director", 200),
    ("GET", "/api/followup/estudiante/1", "director", 200),
    ("GET", "/api/meetings", "director", 200),
    ("GET", "/api/reports/resumen", "director", 200),
    ("GET", "/api/reports/asistencia", "director", 200),
    ("GET", "/api/reports/estudiante/1", "director", 200),
    ("GET", "/api/reports/diario", "director", 200),
    ("GET", "/api/audit", "director", 200),
]


def token(cliente, usuario: str) -> str:
    respuesta = cliente.post(
        "/api/auth/login", json={"nombre_usuario": usuario, "contrasena": "Demo1234!"}
    )
    return respuesta.get_json().get("access_token", "")


def main() -> int:
    app = create_app()
    fallos = 0
    with app.app_context():
        cliente = app.test_client()
        tokens = {rol: token(cliente, usuario) for rol, usuario in ROLES.items()}
        # El login se comprueba con credenciales válidas.
        login = cliente.post(
            "/api/auth/login", json={"nombre_usuario": ROLES["director"], "contrasena": "Demo1234!"}
        )

        print("Comprobando los endpoints de SESCO")
        print("-" * 62)
        for metodo, ruta, rol, esperado in PRUEBAS:
            if rol == "login":
                respuesta = login
            else:
                cabeceras = {"Authorization": f"Bearer {tokens[rol]}"} if rol else {}
                respuesta = cliente.open(ruta, method=metodo, headers=cabeceras)
            marca = "OK " if respuesta.status_code == esperado else "FALLA"
            if respuesta.status_code != esperado:
                fallos += 1
            print(f"  {marca} [{respuesta.status_code}] {metodo:5} {ruta}")

        # El flujo completo: el estudiante muestra su QR y el docente lo registra.
        print("-" * 62)
        print("Flujo de registro por QR")
        # Se parte de cero: si el ingreso ya estaba, la prueba mediría otra cosa.
        _limpiar_asistencia_de_hoy(1)
        codigo = _codigo_del_estudiante(1)
        if codigo is None:
            print("  FALLA no se pudo obtener el código QR del estudiante")
            fallos += 1
        else:
            respuesta = cliente.post(
                "/api/attendance/registrar",
                json={"id_estudiante": 1, "codigo": codigo},
                headers={"Authorization": f"Bearer {tokens['profesor']}"},
            )
            cuerpo = respuesta.get_json() or {}
            if respuesta.status_code in (200, 201):
                print(f"  OK  [{respuesta.status_code}] asistencia: {cuerpo.get('estado')} a las {cuerpo.get('hora_ingreso')}")
            else:
                print(f"  FALLA [{respuesta.status_code}] {cuerpo}")
                fallos += 1

            repetido = cliente.post(
                "/api/attendance/registrar",
                json={"id_estudiante": 1, "codigo": codigo},
                headers={"Authorization": f"Bearer {tokens['profesor']}"},
            )
            if repetido.status_code == 422:
                print("  OK  el mismo código no se acepta dos veces")
            else:
                print(f"  FALLA [{repetido.status_code}] el código se reutilizó")
                fallos += 1

            # La prueba no debe dejar rastros en los datos de demostración.
            _limpiar_asistencia(cuerpo.get("id_asistencia"))

    print("-" * 62)
    if fallos:
        print(f"{fallos} comprobación(es) fallaron.")
        return 1
    print("Todo responde como debe.")
    return 0


def _limpiar_asistencia_de_hoy(id_estudiante: int) -> None:
    """Borra los ingresos de hoy del estudiante para empezar de cero."""
    from sqlalchemy import text

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


def _limpiar_asistencia(id_asistencia) -> None:
    """Borra la asistencia y la lectura que creó la prueba."""
    if not id_asistencia:
        return
    from sqlalchemy import text

    db.session.execute(text("delete from sesco.lecturas_qr where id_asistencia = :id"), {"id": id_asistencia})
    db.session.execute(text("delete from sesco.asistencias where id_asistencia = :id"), {"id": id_asistencia})
    db.session.commit()


def _codigo_del_estudiante(id_estudiante: int) -> str | None:
    credencial = db.session.execute(
        select(CredencialQR).where(
            CredencialQR.id_estudiante == id_estudiante,
            CredencialQR.estado == "activa",
        )
    ).scalars().first()
    if credencial is None:
        return None
    try:
        secreto = descifrar(credencial.secreto_totp_cifrado)
    except Exception:
        return None
    return TOTPService.get_current_code_and_ttl(secreto)[0]


if __name__ == "__main__":
    raise SystemExit(main())
