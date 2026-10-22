"""Esquemas de entrada y salida de los avisos institucionales."""
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class AvisoCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=150)
    contenido: str = Field(min_length=1)
    importante: bool = False
    roles_destinatarios: list[str] = Field(default_factory=list)
    estado: Literal["borrador", "publicado"] = "borrador"


class AvisoUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=150)
    contenido: str | None = Field(default=None, min_length=1)
    importante: bool | None = None
    roles_destinatarios: list[str] | None = None
    estado: Literal["borrador", "publicado", "archivado"] | None = None


class AvisoListQuery(BaseModel):
    estado: Literal["borrador", "publicado", "archivado"] | None = None
    solo_no_leidos: bool = False
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class AvisoInasistenciaCreate(BaseModel):
    id_profesor: int = Field(gt=0)
    id_sesion_clase: int | None = Field(default=None, gt=0)
    fecha_afectada: date
    motivo: str = Field(min_length=3)


def aviso_payload(view) -> dict:
    """Aviso institucional con los datos derivados de la consulta."""
    aviso = view.aviso
    return {
        "id_aviso": aviso.id_aviso,
        "titulo": aviso.titulo,
        "contenido": aviso.contenido,
        "creado_por": aviso.creado_por,
        "publicado_en": aviso.publicado_en.isoformat(timespec="seconds") if aviso.publicado_en else None,
        "importante": bool(aviso.importante),
        "estado": aviso.estado,
        "roles_destinatarios": list(view.roles_destinatarios),
        "leido": bool(view.leido),
        "total_lectores": int(view.total_lectores),
    }


def aviso_inasistencia_payload(aviso) -> dict:
    """Aviso de inasistencia docente."""
    return {
        "id_aviso_docente": aviso.id_aviso_docente,
        "id_profesor": aviso.id_profesor,
        "id_sesion_clase": aviso.id_sesion_clase,
        "fecha_afectada": aviso.fecha_afectada.isoformat(),
        "motivo": aviso.motivo,
        "enviado_en": aviso.enviado_en.isoformat(timespec="seconds") if aviso.enviado_en else None,
        "estado": aviso.estado,
        "revisado_por": aviso.revisado_por,
        "revisado_en": aviso.revisado_en.isoformat(timespec="seconds") if aviso.revisado_en else None,
        "decision": aviso.decision,
    }
