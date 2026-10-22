from sqlalchemy import column, select

from app.core.text.search import normalizar, sin_acentos


def test_normalizar_quita_tildes_y_pasa_a_minusculas():
    assert normalizar("Sofía") == "sofia"
    assert normalizar("CONDORI") == "condori"
    assert normalizar("Nuñez Peña") == "nunez pena"
    assert normalizar("Ángel") == "angel"


def test_normalizar_conserva_las_enie_y_ye():
    # 'ñ' y 'ü' no se descomponen, por eso el mapa SQL los traduce aparte.
    assert normalizar("Nuñez") == "nunez"
    assert normalizar("Güemes") == "guemes"


def test_sin_acentos_genera_una_expresion_sql():
    expresion = sin_acentos(column("nombre"))
    compilada = str(select(expresion).compile(compile_kwargs={"literal_binds": True}))
    assert "lower" in compilada and "translate" in compilada
