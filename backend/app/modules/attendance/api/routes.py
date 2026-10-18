from flask import Blueprint, jsonify, request
from app.modules.auth import auth_required
from app.modules.attendance.services.attendance_service import AttendanceService

bp = Blueprint("attendance", __name__)

@bp.post("/registrar")
@auth_required("profesor", "director")
def registrar_asistencia():
    data = request.get_json() or {}
    id_estudiante = data.get("student_id") or data.get("id_estudiante")
    codigo_qr = data.get("code") or data.get("codigo_qr")

    if not id_estudiante or not codigo_qr:
        return jsonify({"error": "Faltan datos obligatorios (student_id, code)"}), 400

    resultado, status_code = AttendanceService.registrar_ingreso_qr(id_estudiante, str(codigo_qr))
    return jsonify(resultado), status_code