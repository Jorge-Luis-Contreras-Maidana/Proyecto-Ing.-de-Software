from datetime import date

from pydantic import BaseModel, Field

from app.core.http import parse_json, parse_query  # noqa: F401  (se reexporta para las rutas)


class RegistrarQRRequest(BaseModel):
    id_estudiante: int = Field(gt=0)
    codigo: str = Field(min_length=4, max_length=32)
    id_sesion_clase: int | None = Field(default=None, gt=0)


class MarcarManualRequest(BaseModel):
    id_estudiante: int = Field(gt=0)
    estado: str = Field(pattern="^(presente|tarde|ausente|justificada|pendiente)$")
    observacion: str | None = Field(default=None, max_length=500)


class HistorialQuery(BaseModel):
    desde: date | None = None
    hasta: date | None = None


def registro_payload(resultado) -> dict:
    return {
        "id_asistencia": resultado.id_asistencia,
        "id_sesion_clase": resultado.id_sesion_clase,
        "id_estudiante": resultado.id_estudiante,
        "estado": resultado.estado,
        "hora_ingreso": resultado.hora_ingreso.strftime("%H:%M:%S") if resultado.hora_ingreso else None,
        "minutos_retraso": round(resultado.minutos_retraso, 1),
        "ya_registrado": resultado.ya_registrado,
        "mensaje": (
            "El ingreso ya estaba registrado para esta clase."
            if resultado.ya_registrado
            else "Asistencia registrada correctamente."
        ),
    }
