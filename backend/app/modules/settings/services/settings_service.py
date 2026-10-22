"""Reglas de los parámetros de asistencia. No usa Flask ni escribe SQL."""
from dataclasses import dataclass

from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.core.errors.exceptions import NotFound
from app.modules.settings.models.settings import ConfiguracionAsistencia
from app.modules.settings.repositories.settings_repository import SettingsRepository

# Valores por defecto: los mismos que fija el RF cuando aún no hay configuración.
DEFAULTS = {
    "tolerancia_ingreso_min": 5,
    "limite_tardanza_min": 15,
    "ausencias_consecutivas_alerta": 3,
    "tardanzas_mes_alerta": 5,
    "porcentaje_ausencia_alerta": 20,
    "plazo_justificacion_dias": 3,
}

RANGOS = {
    "tolerancia_ingreso_min": (0, 60),
    "limite_tardanza_min": (1, 180),
    "ausencias_consecutivas_alerta": (1, 365),
    "tardanzas_mes_alerta": (1, 365),
    "porcentaje_ausencia_alerta": (0, 100),
    "plazo_justificacion_dias": (0, 90),
}


@dataclass(frozen=True)
class AttendanceSettings:
    id_configuracion: int
    id_unidad: int
    tolerancia_ingreso_min: int
    limite_tardanza_min: int
    ausencias_consecutivas_alerta: int
    tardanzas_mes_alerta: int
    porcentaje_ausencia_alerta: float
    plazo_justificacion_dias: int
    actualizado_en: object | None
    actualizado_por: int | None

    @classmethod
    def from_model(cls, fila: ConfiguracionAsistencia) -> "AttendanceSettings":
        return cls(
            id_configuracion=fila.id_configuracion,
            id_unidad=fila.id_unidad,
            tolerancia_ingreso_min=fila.tolerancia_ingreso_min,
            limite_tardanza_min=fila.limite_tardanza_min,
            ausencias_consecutivas_alerta=fila.ausencias_consecutivas_alerta,
            tardanzas_mes_alerta=fila.tardanzas_mes_alerta,
            porcentaje_ausencia_alerta=float(fila.porcentaje_ausencia_alerta),
            plazo_justificacion_dias=fila.plazo_justificacion_dias,
            actualizado_en=fila.actualizado_en,
            actualizado_por=fila.actualizado_por,
        )


class SettingsService:
    def __init__(self, repo=None):
        self.repo = repo or SettingsRepository()

    def get(self) -> AttendanceSettings:
        """Parámetros vigentes. Si la unidad no los tiene, se usan los valores por defecto."""
        fila = self.repo.first()
        if fila is None:
            return AttendanceSettings(
                id_configuracion=0,
                id_unidad=0,
                actualizado_en=None,
                actualizado_por=None,
                **DEFAULTS,
            )
        return AttendanceSettings.from_model(fila)

    def update(self, principal, cambios: dict) -> AttendanceSettings:
        actual = self.get()
        if actual.id_configuracion == 0:
            raise NotFound(
                "No hay una configuración de asistencia para esta unidad educativa.",
                "Solicite a la dirección que registre los parámetros de la unidad.",
            )
        with unit_of_work():
            fila = self.repo.get_by_unidad(actual.id_unidad)
            for campo, valor in cambios.items():
                if valor is not None:
                    setattr(fila, campo, valor)
            fila.actualizado_en = clock.now()
            fila.actualizado_por = principal.id_usuario
        return self.get()
