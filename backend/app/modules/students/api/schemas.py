from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    codigo_estudiante: str = Field(min_length=1, max_length=25)
    nombres: str = Field(min_length=1, max_length=80)
    apellidos: str = Field(min_length=1, max_length=100)
    fecha_nacimiento: date
    genero: str | None = Field(default=None, max_length=20)
    id_curso: int


class StudentUpdate(BaseModel):
    nombres: str | None = Field(default=None, min_length=1, max_length=80)
    apellidos: str | None = Field(default=None, min_length=1, max_length=100)
    fecha_nacimiento: date | None = None
    genero: str | None = Field(default=None, max_length=20)
    id_curso: int | None = None


class StudentListQuery(BaseModel):
    q: str | None = Field(default=None, max_length=80)
    id_curso: int | None = None
    estado: Literal["activo", "retirado", "egresado", "todos"] = "activo"
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=50)


class ObservationCreate(BaseModel):
    tipo: Literal["academica", "asistencia", "comportamiento", "convivencia", "otra"]
    descripcion: str = Field(min_length=1, max_length=2000)
    confidencial: bool = False


class GuardianLinkCreate(BaseModel):
    id_tutor: int
    parentesco: str = Field(min_length=1, max_length=30)
    es_contacto_principal: bool = False


def student_payload(view, tutores=None) -> dict:
    est, curso = view.estudiante, view.curso
    data = {
        "id_estudiante": est.id_estudiante,
        "codigo_estudiante": est.codigo_estudiante,
        "nombres": est.nombres,
        "apellidos": est.apellidos,
        "fecha_nacimiento": est.fecha_nacimiento.isoformat(),
        "genero": est.genero,
        "estado": est.estado,
        "curso": None
        if curso is None
        else {
            "id_curso": curso.id_curso,
            "nivel": curso.nivel,
            "grado": curso.grado,
            "paralelo": curso.paralelo,
            "turno": curso.turno,
        },
    }
    if tutores is not None:
        data["tutores"] = tutores
    return data


def observation_payload(o) -> dict:
    return {
        "id_observacion": o.id_observacion,
        "tipo": o.tipo,
        "descripcion": o.descripcion,
        "confidencial": o.confidencial,
        "registrada_por": o.registrada_por,
        "fecha_hora": o.fecha_hora.isoformat(timespec="seconds"),
    }
