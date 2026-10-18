"""Asigna una contraseña de demostración real (Argon2) a los usuarios que aún tienen el marcador DEMO.

Uso (desde la carpeta backend, con el entorno virtual activado):
    python ../scripts/seed_passwords.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import text  # noqa: E402

from app import create_app  # noqa: E402
from app.core.security.hashing import hash_password  # noqa: E402
from app.extensions import db  # noqa: E402

PASSWORD_DEMO = "Demo1234!"

app = create_app()
with app.app_context():
    resultado = db.session.execute(
        text("UPDATE sesco.usuarios SET hash_contrasena = :h WHERE hash_contrasena = 'DEMO_HASH_CAMBIAR_EN_APLICACION'"),
        {"h": hash_password(PASSWORD_DEMO)},
    )
    db.session.commit()
    print(f"Usuarios actualizados: {resultado.rowcount}. Contraseña de demostración: {PASSWORD_DEMO}")