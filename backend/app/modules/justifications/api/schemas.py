from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from app.core.http import parse_json, parse_query  # noqa: F401  (se reexporta para las rutas)


class JustificacionCreate(BaseModel):
    id_estudiante: int = Field(gt=0)
    fecha_inicio: date
    fecha_fin: date
    motivo: str = Field(min_length=3, max_length=2000)
    documento_referencia: str | None = Field(default=None, max_length=500)


class JustificacionEstado(BaseModel):
    estado: Literal["pendiente", "avisada", "justificada", "no_justificada", "requiere_informacion"]
    comentario: str | None = Field(default=None, max_length=2000)


class JustificacionListQuery(BaseModel):
    estado: str | None = Field(default=None, max_length=20)
    id_estudiante: int | None = Field(default=None, gt=0)


def justificacion_payload(j) -> dict:
    return {
        "id_justificacion": j.id_justificacion,
        "id_estudiante": j.id_estudiante,
        "id_tutor": j.id_tutor,
        "fecha_inicio": j.fecha_inicio.isoformat(),
        "fecha_fin": j.fecha_fin.isoformat(),
        "motivo": j.motivo_declarado,
        "documento_referencia": j.documento_referencia,
        "solicitada_en": j.solicitada_en.isoformat(timespec="seconds") if j.solicitada_en else None,
        "estado": j.estado,
        "revisada_por": j.revisada_por,
        "revisada_en": j.revisada_en.isoformat(timespec="seconds") if j.revisada_en else None,
        "comentario_revision": j.comentario_revision,
    }
