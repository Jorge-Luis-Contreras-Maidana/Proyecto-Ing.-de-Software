"""Reglas de clasificación de la asistencia: funciones puras, sin base de datos."""
from datetime import date, datetime, time

from app.modules.attendance.services.attendance_rules import (
    AUSENTE,
    JUSTIFICADA,
    PRESENTE,
    TARDE,
    clasificar,
    dentro_de_plazo,
    minutos_de_retraso,
    resumen,
)


def test_los_minutos_de_retraso_se_miden_desde_el_inicio_previsto():
    inicio = time(8, 0)
    assert minutos_de_retraso(inicio, datetime(2026, 3, 2, 8, 0)) == 0
    assert minutos_de_retraso(inicio, datetime(2026, 3, 2, 8, 7)) == 7
    assert minutos_de_retraso(inicio, datetime(2026, 3, 2, 8, 45)) == 45


def test_llegar_antes_de_la_hora_da_un_retraso_negativo():
    assert minutos_de_retraso(time(8, 0), datetime(2026, 3, 2, 7, 50)) == -10


def test_dentro_de_la_tolerancia_es_presente():
    assert clasificar(time(8, 0), datetime(2026, 3, 2, 8, 3), 5, 15) == PRESENTE
    assert clasificar(time(8, 0), datetime(2026, 3, 2, 7, 55), 5, 15) == PRESENTE


def test_entre_la_tolerancia_y_el_limite_es_tarde():
    assert clasificar(time(8, 0), datetime(2026, 3, 2, 8, 6), 5, 15) == TARDE
    assert clasificar(time(8, 0), datetime(2026, 3, 2, 8, 15), 5, 15) == TARDE


def test_pasado_el_limite_es_ausente():
    assert clasificar(time(8, 0), datetime(2026, 3, 2, 8, 21), 5, 15) == AUSENTE
    assert clasificar(time(8, 0), datetime(2026, 3, 2, 9, 0), 5, 15) == AUSENTE


def test_el_plazo_de_justificacion():
    hoy = date(2026, 3, 10)
    assert dentro_de_plazo(date(2026, 3, 8), hoy, 3) is True
    assert dentro_de_plazo(date(2026, 3, 6), hoy, 3) is False
    assert dentro_de_plazo(date(2026, 1, 1), hoy, 0) is True  # sin plazo


def test_el_resumen_suma_los_totales():
    conteos = {PRESENTE: 10, TARDE: 3, AUSENTE: 2, JUSTIFICADA: 1}
    resultado = resumen(conteos)
    assert resultado["total"] == 16
    assert resultado["presentes"] == 10
    assert resultado["tardanzas"] == 3
    assert resultado["ausencias"] == 2
    assert resultado["justificadas"] == 1
    assert resultado["pendientes"] == 0
