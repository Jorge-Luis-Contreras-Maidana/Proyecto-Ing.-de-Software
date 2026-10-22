"""Detección de patrones de inasistencia que originan alertas de seguimiento.

El detector no escribe SQL ni guarda nada: recibe los datos ya leídos del
repositorio, aplica los parámetros de `configuracion_asistencia` y devuelve los
patrones encontrados. El servicio de seguimiento decide qué alertas crea.
"""
from dataclasses import dataclass
from datetime import date

from app.core import clock
from app.modules.followup.repositories.followup_repository import FollowupRepository
from app.modules.settings.services.settings_service import SettingsService

# Estados que la base de datos admite como tipo de alerta.
TIPO_AUSENCIAS = "ausencias_consecutivas"
TIPO_TARDANZAS = "tardanzas_reiteradas"
TIPO_PORCENTAJE = "porcentaje_ausencia"

ESTADO_AUSENTE = "ausente"
ESTADO_TARDE = "tarde"
ESTADO_PENDIENTE = "pendiente"

MESES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


@dataclass(frozen=True)
class Patron:
    """Patrón detectado: un estudiante que cumple una condición de alerta."""

    id_estudiante: int
    id_curso: int
    tipo: str
    descripcion: str
    valor: int = 0  # magnitud del patrón, sirve para ordenar


class PatternDetector:
    """Recorre las asistencias de la gestión activa y detecta patrones."""

    def __init__(self, repo=None, settings=None):
        self.repo = repo or FollowupRepository()
        self.settings = settings or SettingsService()

    def detectar(self, hoy: date | None = None) -> list[Patron]:
        """Patrones detectados en la gestión escolar activa."""
        dia = hoy or clock.now().date()
        gestion = self.repo.active_gestion()
        if gestion is None:
            return []

        parametros = self.settings.get()
        filas = self.repo.asistencias_de_gestion(gestion.id_gestion, dia)
        grupos = self._agrupar(filas)

        patrones: list[Patron] = []
        patrones.extend(self._ausencias_consecutivas(grupos, parametros.ausencias_consecutivas_alerta))
        patrones.extend(self._tardanzas_del_mes(grupos, parametros.tardanzas_mes_alerta))
        patrones.extend(
            self._porcentaje_de_ausencia(grupos, float(parametros.porcentaje_ausencia_alerta))
        )

        # El patrón más fuerte de cada estudiante y tipo va primero.
        patrones.sort(key=lambda p: (p.id_estudiante, p.tipo, -p.valor))
        return patrones

    # ---------- apoyo ----------
    @staticmethod
    def _agrupar(filas) -> dict[tuple[int, int], list[tuple]]:
        """Agrupa las asistencias por estudiante y curso, en orden de fecha."""
        grupos: dict[tuple[int, int], list[tuple]] = {}
        for id_estudiante, id_curso, fecha, hora, estado in filas:
            grupos.setdefault((id_estudiante, id_curso), []).append((fecha, hora, estado))
        return grupos

    @staticmethod
    def _evaluadas(registros: list[tuple]) -> list[tuple]:
        """Clases ya registradas: las pendientes no dicen nada del estudiante."""
        return [registro for registro in registros if registro[2] != ESTADO_PENDIENTE]

    # ---------- reglas ----------
    def _ausencias_consecutivas(self, grupos, minimo: int) -> list[Patron]:
        """N o más ausencias seguidas del mismo estudiante."""
        patrones: list[Patron] = []
        if minimo <= 0:
            return patrones
        for (id_estudiante, id_curso), registros in grupos.items():
            racha = 0
            inicio = None
            mejor = (0, None, None)
            for fecha, _hora, estado in self._evaluadas(registros):
                if estado == ESTADO_AUSENTE:
                    if racha == 0:
                        inicio = fecha
                    racha += 1
                    if racha > mejor[0]:
                        mejor = (racha, inicio, fecha)
                else:
                    racha = 0
                    inicio = None
            if mejor[0] >= minimo:
                racha, inicio, fin = mejor
                patrones.append(
                    Patron(
                        id_estudiante=id_estudiante,
                        id_curso=id_curso,
                        tipo=TIPO_AUSENCIAS,
                        descripcion=(
                            f"{racha} ausencias consecutivas entre {inicio.isoformat()} "
                            f"y {fin.isoformat()}."
                        ),
                        valor=racha,
                    )
                )
        return patrones

    def _tardanzas_del_mes(self, grupos, minimo: int) -> list[Patron]:
        """N o más tardanzas dentro del mismo mes."""
        patrones: list[Patron] = []
        if minimo <= 0:
            return patrones
        conteo: dict[tuple[int, int, int, int], int] = {}
        for (id_estudiante, id_curso), registros in grupos.items():
            for fecha, _hora, estado in registros:
                if estado != ESTADO_TARDE:
                    continue
                clave = (id_estudiante, id_curso, fecha.year, fecha.month)
                conteo[clave] = conteo.get(clave, 0) + 1
        for (id_estudiante, id_curso, anio, mes), total in conteo.items():
            if total < minimo:
                continue
            patrones.append(
                Patron(
                    id_estudiante=id_estudiante,
                    id_curso=id_curso,
                    tipo=TIPO_TARDANZAS,
                    descripcion=f"{total} tardanzas registradas en {MESES[mes - 1]} de {anio}.",
                    valor=total,
                )
            )
        return patrones

    def _porcentaje_de_ausencia(self, grupos, limite: float) -> list[Patron]:
        """Porcentaje de ausencias del período por encima del parámetro."""
        patrones: list[Patron] = []
        for (id_estudiante, id_curso), registros in grupos.items():
            evaluadas = self._evaluadas(registros)
            total = len(evaluadas)
            if total == 0:
                continue
            ausencias = sum(1 for registro in evaluadas if registro[2] == ESTADO_AUSENTE)
            porcentaje = round(ausencias * 100.0 / total, 2)
            if porcentaje <= limite:
                continue
            patrones.append(
                Patron(
                    id_estudiante=id_estudiante,
                    id_curso=id_curso,
                    tipo=TIPO_PORCENTAJE,
                    descripcion=(
                        f"{porcentaje}% de ausencias ({ausencias} de {total} clases) por encima "
                        f"del {limite}% configurado."
                    ),
                    valor=ausencias,
                )
            )
        return patrones
