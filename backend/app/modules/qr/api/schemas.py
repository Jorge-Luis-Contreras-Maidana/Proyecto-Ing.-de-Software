from pydantic import BaseModel, Field

from app.core.http import parse_json  # noqa: F401  (se reexporta para las rutas)


class QRVerifyRequest(BaseModel):
    id_estudiante: int = Field(gt=0)
    codigo: str = Field(min_length=4, max_length=32)


class QRScanRequest(BaseModel):
    """Lo que llega del lector: puede traer el JSON de la app o solo el código."""

    id_estudiante: int | None = Field(default=None, gt=0)
    codigo: str = Field(min_length=4, max_length=200)


def qr_payload(resultado) -> dict:
    return {
        "id_estudiante": resultado.id_estudiante,
        "id_credencial": resultado.id_credencial,
        "codigo": resultado.code,
        "expira_en_segundos": resultado.expires_in,
        "imagen": f"data:image/png;base64,{resultado.imagen_base64}",
    }
