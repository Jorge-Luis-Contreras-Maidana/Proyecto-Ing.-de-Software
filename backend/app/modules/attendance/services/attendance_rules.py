"""Reglas de clasificación de la asistencia. Funciones puras, sin base de datos."""
from datetime import date, datetime, time, timedelta

# Estados posibles de una asistencia (los mismos que admite la tabla 'asistencias').
PRESENTE = "presente"
TARDE = "tarde"
AUSENTE = "ausente"
JUSTIFICADA = "justificada"
PENDIENTE = "pendiente"


def minutos_de_retraso(hora_inicio: time, momento: datetime) -> float:
    """Minutos transcurridos entre el inicio previsto y el ingreso.

    Si el estudiante llega antes de la hora, el resultado es negativo y cuenta
    como puntual.
    """
    inicio = datetime.combine(momento.date(), hora_inicio)
    return (momento - inicio).total_seconds() / 60.0


def clasificar(
    hora_inicio: time,
    momento: datetime,
    tolerancia_min: int,
    limite_tardanza_min: int,
) -> str:
    """Clasifica el ingreso según los parámetros de la unidad educativa.

    - dentro de la tolerancia      -> presente
    - entre la tolerancia y el límite -> tarde
    - pasado el límite             -> ausente
    """
    if momento is None:
        return PENDIENTE
    retraso = minutos_de_retraso(hora_inicio, momento)
    if retraso <= tolerancia_min:
        return PRESENTE
    if retraso <= limite_tardanza_min:
        return TARDE
    return AUSENTE


def dentro_de_plazo(fecha_ausencia: date, hoy: date, plazo_dias: int) -> bool:
    """True si la justificación aún está dentro del plazo configurado."""
    if plazo_dias <= 0:
        return True
    return fecha_ausencia >= hoy - timedelta(days=plazo_dias)


def resumen(estados: dict[str, int]) -> dict:
    """Conteos por estado más los totales que usa la interfaz."""
    total = sum(estados.values())
    return {
        "total": total,
        "presentes": estados.get(PRESENTE, 0),
        "tardanzas": estados.get(TARDE, 0),
        "ausencias": estados.get(AUSENTE, 0),
        "justificadas": estados.get(JUSTIFICADA, 0),
        "pendientes": estados.get(PENDIENTE, 0),
    }
