"""Genera la programación de clases y las asistencias pendientes.

Uso (desde la carpeta backend, con el entorno virtual activado):
    python ../scripts/seed_sesiones.py --dias 20
    python ../scripts/seed_sesiones.py --desde 2026-10-21 --dias 5
    python ../scripts/seed_sesiones.py --base sesco_test
"""
import argparse
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))
sys.path.insert(0, str(RAIZ / "scripts"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera sesiones de clase y asistencias pendientes.")
    parser.add_argument("--desde", type=date.fromisoformat, default=None, help="Fecha inicial (por defecto, hoy).")
    parser.add_argument("--dias", type=int, default=20, help="Cantidad de días lectivos a programar.")
    parser.add_argument("--sin-asistencias", action="store_true", help="Solo crea las sesiones.")
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
    from app.extensions import db
    from app.modules.attendance.models.attendance import SesionClase
    from app.modules.attendance.services.schedule_service import ScheduleService

    app = create_app()
    with app.app_context():
        desde = args.desde or clock.now().date()
        resultado = ScheduleService().generar(desde, args.dias, crear_asistencias=not args.sin_asistencias)
        total = db.session.execute(
            select(SesionClase.id_sesion_clase).where(SesionClase.fecha >= desde)
        ).all()
        print(
            f"Sesiones nuevas: {resultado['sesiones_creadas']}. "
            f"Sesiones programadas desde {desde}: {len(total)}."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
