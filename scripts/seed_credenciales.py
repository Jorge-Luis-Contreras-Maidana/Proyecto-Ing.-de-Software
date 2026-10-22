"""Emite credenciales QR reales para los estudiantes que aún no tienen una válida.

El script de demostración deja marcadores de texto en 'credenciales_qr'. Este
script los reemplaza por secretos TOTP de verdad, cifrados con la clave
TOTP_ENCRYPTION_KEY, de modo que la aplicación pueda descifrarlos.

También reemite las credenciales que ya no se pueden descifrar (por ejemplo, si
se cambió la clave de cifrado).

Uso (desde la carpeta backend, con el entorno virtual activado):
    python ../scripts/seed_credenciales.py
    python ../scripts/seed_credenciales.py --base sesco_test
"""
import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))
sys.path.insert(0, str(RAIZ / "scripts"))

MARCADOR = "DEMO_SECRETO_CIFRADO_"


def main() -> int:
    parser = argparse.ArgumentParser(description="Emite credenciales QR reales a los estudiantes.")
    parser.add_argument("--base", default=None, help="Base de datos destino (por defecto, DATABASE_URL del .env).")
    args = parser.parse_args()

    # La base debe cambiarse antes de importar la aplicación: la configuración
    # lee DATABASE_URL al importarse.
    if args.base:
        from _entorno import usar_base

        usar_base(args.base)

    from sqlalchemy import select

    from app import create_app
    from app.core import clock
    from app.core.errors.exceptions import InvalidData
    from app.core.security.totp_crypto import cifrar, descifrar
    from app.extensions import db
    from app.modules.qr.models.qr import CredencialQR
    from app.modules.qr.services.totp_service import TOTPService
    from app.modules.students.models.students import Estudiante

    def es_utilizable(credencial) -> bool:
        """True si la credencial es real y se puede descifrar con la clave actual."""
        if credencial.secreto_totp_cifrado.startswith(MARCADOR):
            return False
        try:
            descifrar(credencial.secreto_totp_cifrado)
        except InvalidData:
            return False
        return True

    app = create_app()
    with app.app_context():
        students = db.session.execute(select(Estudiante).order_by(Estudiante.id_estudiante)).scalars().all()
        creadas = 0
        revocadas = 0
        for estudiante in students:
            credenciales = db.session.execute(
                select(CredencialQR).where(CredencialQR.id_estudiante == estudiante.id_estudiante)
            ).scalars().all()
            vigente = None
            for credencial in credenciales:
                if credencial.estado == "activa" and es_utilizable(credencial):
                    vigente = credencial
                    break
            if vigente is not None:
                continue
            for credencial in credenciales:
                if credencial.estado == "activa":
                    credencial.estado = "revocada"
                    credencial.revocada_en = clock.now()
                    revocadas += 1
            db.session.add(
                CredencialQR(
                    id_estudiante=estudiante.id_estudiante,
                    secreto_totp_cifrado=cifrar(TOTPService.generate_secret()),
                    emitida_en=clock.now(),
                    estado="activa",
                )
            )
            creadas += 1
        db.session.commit()
        print(f"Credenciales emitidas: {creadas}. Credenciales inservibles revocadas: {revocadas}.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
