"""Búsqueda de texto insensible a acentos y mayúsculas.

En Bolivia los nombres llevan tildes ("Sofía", "Condori"), por lo que comparar
con ILIKE directamente hace que "sofia" no encuentre "Sofía". Aquí se normaliza
el texto en Python (minúsculas sin tildes) y en SQL (translate + lower), de modo
que ambas partes de la comparación quedan en el mismo alfabeto.
"""
import unicodedata

from sqlalchemy import func

# Pares alineados posición a posición: PostgreSQL traduce carácter por carácter.
# Si un carácter de _MAP_ORIGEN no tiene equivalente en _MAP_DESTINO, se elimina.
_MAP_ORIGEN = "áàäâãéèëêíìïîóòöôõúùüûñç"
_MAP_DESTINO = "aaaaaeeeeiiiiooooouuuunc"


def normalizar(texto: str) -> str:
    """Texto en minúsculas y sin tildes, para comparar en Python."""
    descompuesto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def sin_acentos(columna):
    """Expresión SQL que deja una columna en minúsculas y sin tildes.

    El orden importa: primero se pasa a minúsculas y después se traducen las
    tildes. Al revés, una 'Ñ' mayúscula no estaría en el mapa y sobreviviría
    al translate, dando un resultado distinto al de normalizar() en Python.
    """
    return func.translate(func.lower(columna), _MAP_ORIGEN, _MAP_DESTINO)


def coincide(columna, texto: str):
    """Condición SQL: la columna contiene el texto, ignorando tildes y mayúsculas.

    `columna` puede ser una columna o cualquier expresión de SQLAlchemy.
    """
    return sin_acentos(columna).contains(normalizar(texto), autoescape=True)
