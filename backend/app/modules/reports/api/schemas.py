"""Esquemas de entrada y salida del módulo de reportes."""
from datetime import date

from pydantic import BaseModel, Field


class ReporteAsistenciaQuery(BaseModel):
    desde: date | None = None
    hasta: date | None = None
    id_curso: int | None = Field(default=None, gt=0)
    id_estudiante: int | None = Field(default=None, gt=0)


class ReporteDiarioQuery(BaseModel):
    fecha: date | None = None
