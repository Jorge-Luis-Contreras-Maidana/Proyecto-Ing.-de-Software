"""Esquemas de entrada y salida de la bitácora de auditoría."""
from datetime import date

from pydantic import BaseModel, Field


class AuditListQuery(BaseModel):
    operacion: str | None = Field(default=None, max_length=50)
    entidad: str | None = Field(default=None, max_length=60)
    id_usuario: int | None = Field(default=None, gt=0)
    desde: date | None = None
    hasta: date | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=100)


def evento_payload(evento) -> dict:
    """Evento registrado en la bitácora."""
    return {
        "id_evento": evento.id_evento,
        "id_usuario": evento.id_usuario,
        "operacion": evento.operacion,
        "entidad": evento.entidad,
        "id_registro": evento.id_registro,
        "fecha_hora": evento.fecha_hora.isoformat(timespec="seconds") if evento.fecha_hora else None,
        "direccion_ip": str(evento.direccion_ip) if evento.direccion_ip else None,
        "detalle": evento.detalle,
    }
