"""Compara los modelos SQLAlchemy con el esquema real de la base de datos.

Uso (desde la carpeta backend, con el entorno virtual activado):
    python ../scripts/verificar_modelos.py

Salida: una lista de diferencias. Si no imprime nada, los modelos coinciden
con el esquema.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import inspect  # noqa: E402

from app import create_app  # noqa: E402
from app.core.database.base import metadata  # noqa: E402
from app.extensions import db  # noqa: E402

# Los modelos se registran al importarlos.
import app.modules.attendance.models.attendance  # noqa: E402,F401
import app.modules.announcements.models.announcements  # noqa: E402,F401
import app.modules.audit.models.audit  # noqa: E402,F401
import app.modules.auth.models.auth  # noqa: E402,F401
import app.modules.followup.models.followup  # noqa: E402,F401
import app.modules.justifications.models.justification  # noqa: E402,F401
import app.modules.meetings.models.meetings  # noqa: E402,F401
import app.modules.notifications.models.notifications  # noqa: E402,F401
import app.modules.qr.models.qr  # noqa: E402,F401
import app.modules.settings.models.settings  # noqa: E402,F401
import app.modules.students.models.guardian_link  # noqa: E402,F401
import app.modules.students.models.students  # noqa: E402,F401


def main() -> int:
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        tablas_sql = {
            t for t in inspector.get_table_names(schema="sesco")
            if not t.startswith("v_")
        }
        # metadata usa la clave "sesco.nombre"; el inspector devuelve el nombre pelado.
        tablas_modelo = {t.split(".", 1)[-1] for t in metadata.tables.keys()}

        problemas: list[str] = []

        for tabla in sorted(tablas_modelo - tablas_sql):
            problemas.append(f"El modelo '{tabla}' no existe en la base de datos.")
        for tabla in sorted(tablas_sql - tablas_modelo):
            problemas.append(f"La tabla '{tabla}' de la base de datos no tiene modelo.")

        for tabla in sorted(tablas_modelo & tablas_sql):
            columnas_sql = {c["name"] for c in inspector.get_columns(tabla, schema="sesco")}
            columnas_modelo = {c.name for c in metadata.tables[f"sesco.{tabla}"].columns}
            for columna in sorted(columnas_sql - columnas_modelo):
                problemas.append(f"{tabla}.{columna}: falta en el modelo.")
            for columna in sorted(columnas_modelo - columnas_sql):
                problemas.append(f"{tabla}.{columna}: el modelo la declara pero no existe en la base.")

        if problemas:
            print("DIFERENCIAS ENCONTRADAS:")
            for p in problemas:
                print("  -", p)
            return 1
        print(f"OK: {len(tablas_modelo)} tablas del modelo coinciden con el esquema 'sesco'.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
