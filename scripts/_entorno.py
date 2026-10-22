"""Utilidades compartidas por los scripts de la carpeta scripts."""
import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

RAIZ = Path(__file__).resolve().parents[1]


def usar_base(nombre: str) -> None:
    """Apunta DATABASE_URL a otra base de datos del mismo servidor.

    Debe llamarse antes de importar 'app', porque la configuración lee la
    variable de entorno al importarse.
    """
    from dotenv import load_dotenv

    load_dotenv(RAIZ / "backend" / ".env")
    actual = os.environ.get("DATABASE_URL", "")
    if not actual:
        raise SystemExit("No se encontró DATABASE_URL en backend/.env.")
    partes = urlsplit(actual)
    os.environ["DATABASE_URL"] = urlunsplit(
        (partes.scheme, partes.netloc, "/" + nombre, partes.query, partes.fragment)
    )
