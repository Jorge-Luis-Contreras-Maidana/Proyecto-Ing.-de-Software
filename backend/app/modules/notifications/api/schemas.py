"""Esquemas de entrada y salida de las notificaciones."""
from typing import Literal

from pydantic import BaseModel, Field


class NotificacionCreate(BaseModel):
    id_usuario_destinatario: int = Field(gt=0)
    tipo: Literal[
        "ausencia_estudiante",
        "tardanza_estudiante",
        "salida_estudiante",
        "salida_anticipada",
        "citacion",
        "aviso",
        "otro",
    ]
    titulo: str = Field(min_length=1, max_length=150)
    mensaje: str = Field(min_length=1)
    entidad_referencia: str | None = Field(default=None, max_length=40)
    id_referencia: int | None = None


class NotificacionListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


def notificacion_payload(notificacion) -> dict:
    """Notificación dirigida a un usuario."""
    return {
        "id_notificacion": notificacion.id_notificacion,
        "id_usuario_destinatario": notificacion.id_usuario_destinatario,
        "tipo": notificacion.tipo,
        "titulo": notificacion.titulo,
        "mensaje": notificacion.mensaje,
        "creada_en": notificacion.creada_en.isoformat(timespec="seconds") if notificacion.creada_en else None,
        "entregada_en": notificacion.entregada_en.isoformat(timespec="seconds") if notificacion.entregada_en else None,
        "leida_en": notificacion.leida_en.isoformat(timespec="seconds") if notificacion.leida_en else None,
        "estado": notificacion.estado,
        "entidad_referencia": notificacion.entidad_referencia,
        "id_referencia": notificacion.id_referencia,
    }
