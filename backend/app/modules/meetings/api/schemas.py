"""Esquemas de entrada y salida del módulo de citas."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

EstadoCitacion = Literal["programada", "confirmada", "realizada", "cancelada", "reprogramada"]


class CitacionListQuery(BaseModel):
    estado: EstadoCitacion | None = None
    id_estudiante: int | None = Field(default=None, gt=0)


class CitacionCreate(BaseModel):
    id_estudiante: int = Field(gt=0)
    id_tutor: int = Field(gt=0)
    id_profesor: int = Field(gt=0)
    id_alerta: int | None = Field(default=None, gt=0)
    fecha_hora: datetime
    motivo: str = Field(min_length=1, max_length=2000)
    observaciones: str | None = Field(default=None, max_length=2000)


class CitacionEstadoUpdate(BaseModel):
    estado: EstadoCitacion
    observaciones: str | None = Field(default=None, max_length=2000)


def citacion_payload(citacion) -> dict:
    """Cita de seguimiento en el formato del contrato de API."""
    return {
        "id_citacion": citacion.id_citacion,
        "id_estudiante": citacion.id_estudiante,
        "id_tutor": citacion.id_tutor,
        "id_profesor": citacion.id_profesor,
        "id_alerta": citacion.id_alerta,
        "fecha_hora": citacion.fecha_hora.isoformat(timespec="seconds") if citacion.fecha_hora else None,
        "motivo": citacion.motivo,
        "estado": citacion.estado,
        "creada_en": citacion.creada_en.isoformat(timespec="seconds") if citacion.creada_en else None,
        "observaciones": citacion.observaciones,
    }
