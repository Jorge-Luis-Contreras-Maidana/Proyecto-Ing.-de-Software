"""Esquemas de entrada y salida del módulo de seguimiento."""
from typing import Literal

from pydantic import BaseModel, Field

TipoAlerta = Literal["ausencias_consecutivas", "tardanzas_reiteradas", "porcentaje_ausencia", "otra"]
EstadoAlerta = Literal["abierta", "en_seguimiento", "resuelta", "descartada"]


class AlertaListQuery(BaseModel):
    estado: EstadoAlerta | None = None
    id_estudiante: int | None = Field(default=None, gt=0)
    id_curso: int | None = Field(default=None, gt=0)


class AlertaCreate(BaseModel):
    id_estudiante: int = Field(gt=0)
    id_curso: int = Field(gt=0)
    tipo: TipoAlerta
    descripcion: str = Field(min_length=1, max_length=2000)
    asignada_a: int | None = Field(default=None, gt=0)


class AlertaEstadoUpdate(BaseModel):
    estado: EstadoAlerta
    observacion: str | None = Field(default=None, max_length=2000)


def alerta_payload(alerta) -> dict:
    """Alerta de seguimiento en el formato del contrato de API."""
    return {
        "id_alerta": alerta.id_alerta,
        "id_estudiante": alerta.id_estudiante,
        "id_curso": alerta.id_curso,
        "tipo": alerta.tipo,
        "descripcion": alerta.descripcion,
        "generada_en": alerta.generada_en.isoformat(timespec="seconds") if alerta.generada_en else None,
        "estado": alerta.estado,
        "asignada_a": alerta.asignada_a,
        "resuelta_en": alerta.resuelta_en.isoformat(timespec="seconds") if alerta.resuelta_en else None,
        "observacion": alerta.observacion,
    }
