from pydantic import BaseModel, Field

from app.core.http import parse_json  # noqa: F401  (se reexporta para las rutas)


class SettingsUpdate(BaseModel):
    tolerancia_ingreso_min: int | None = Field(default=None, ge=0, le=60)
    limite_tardanza_min: int | None = Field(default=None, ge=1, le=180)
    ausencias_consecutivas_alerta: int | None = Field(default=None, ge=1, le=365)
    tardanzas_mes_alerta: int | None = Field(default=None, ge=1, le=365)
    porcentaje_ausencia_alerta: float | None = Field(default=None, ge=0, le=100)
    plazo_justificacion_dias: int | None = Field(default=None, ge=0, le=90)


def settings_payload(cfg) -> dict:
    return {
        "id_configuracion": cfg.id_configuracion,
        "id_unidad": cfg.id_unidad,
        "tolerancia_ingreso_min": cfg.tolerancia_ingreso_min,
        "limite_tardanza_min": cfg.limite_tardanza_min,
        "ausencias_consecutivas_alerta": cfg.ausencias_consecutivas_alerta,
        "tardanzas_mes_alerta": cfg.tardanzas_mes_alerta,
        "porcentaje_ausencia_alerta": cfg.porcentaje_ausencia_alerta,
        "plazo_justificacion_dias": cfg.plazo_justificacion_dias,
        "actualizado_en": cfg.actualizado_en.isoformat(timespec="seconds") if cfg.actualizado_en else None,
        "actualizado_por": cfg.actualizado_por,
    }
