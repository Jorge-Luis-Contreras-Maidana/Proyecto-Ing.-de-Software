from flask import Blueprint

from app.modules.attendance.api.schemas import (
    HistorialQuery,
    MarcarManualRequest,
    RegistrarQRRequest,
    parse_json,
    parse_query,
    registro_payload,
)
from app.modules.attendance.services.attendance_service import AttendanceService
from app.modules.auth import auth_required, current_principal

bp = Blueprint("attendance", __name__)


def _service() -> AttendanceService:
    return AttendanceService()


@bp.post("/registrar")
@auth_required("profesor", "director")
def registrar_asistencia():
    """Registra el ingreso de un estudiante a partir de su credencial QR."""
    data = parse_json(RegistrarQRRequest)
    resultado = _service().registrar_por_qr(
        current_principal(),
        data.id_estudiante,
        data.codigo,
        data.id_sesion_clase,
    )
    return registro_payload(resultado), 200 if resultado.ya_registrado else 201


@bp.get("/hoy")
@auth_required("profesor", "director")
def sesiones_de_hoy():
    """Sesiones programadas hoy con el conteo de asistencia."""
    return {"items": _service().hoy(current_principal())}


@bp.get("/sesion/<int:id_sesion_clase>")
@auth_required("profesor", "director")
def detalle_sesion(id_sesion_clase: int):
    """Estado de asistencia de cada estudiante de la sesión."""
    return _service().sesion(current_principal(), id_sesion_clase)


@bp.post("/sesion/<int:id_sesion_clase>/marcar")
@auth_required("profesor", "director")
def marcar_manual(id_sesion_clase: int):
    """Registro manual de la asistencia, sin escanear el QR."""
    data = parse_json(MarcarManualRequest)
    asistencia = _service().marcar_manual(
        current_principal(),
        id_sesion_clase,
        data.id_estudiante,
        data.estado,
        data.observacion,
    )
    return {
        "id_asistencia": asistencia.id_asistencia,
        "id_sesion_clase": id_sesion_clase,
        "id_estudiante": asistencia.id_estudiante,
        "estado": asistencia.estado,
        "mensaje": "Asistencia registrada correctamente.",
    }


@bp.get("/estudiante/<int:id_estudiante>")
@auth_required()
def historial(id_estudiante: int):
    """Historial de asistencia de un estudiante."""
    f = parse_query(HistorialQuery)
    return {"items": _service().historial(current_principal(), id_estudiante, f.desde, f.hasta)}
