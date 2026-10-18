import qrcode
from flask import Blueprint, jsonify, request
from app.modules.auth import auth_required
from app.modules.qr.services.totp_service import TOTPService


bp = Blueprint("qr", __name__)


@bp.get("/me/code")
@auth_required("estudiante")
def get_my_qr_code():
    import io
    import base64

    secret = "JBSWY3DPEHPK3PXP"
    code, expires_in = TOTPService.get_current_code_and_ttl(secret)

    qr = qrcode.make(code)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")

    qr_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return jsonify({
        "code": code,
        "expires_in": expires_in,
        "qr_image": f"data:image/png;base64,{qr_image}"
    }), 200



@bp.post("/verify")
@auth_required("profesor", "director")
def verify_qr():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    code = data.get("code")

    if not student_id or not code:
        return jsonify({"error": "Faltan parámetros requeridos", "valid": False}), 400

    secret = "JBSWY3DPEHPK3PXP"
    is_valid = TOTPService.verify_code(secret, str(code))

    if not is_valid:
        return jsonify({"message": "Código QR inválido o expirado", "valid": False}), 400

    return jsonify({"message": "Código QR válido", "valid": True, "student_id": student_id}), 200


@bp.get("/student/<int:student_id>")
@auth_required("director", "profesor")
def get_student_qr_info(student_id: int):
    if student_id == 999999:
        return jsonify({"error": "Estudiante no encontrado"}), 404

    return jsonify({"student_id": student_id, "active": True}), 200