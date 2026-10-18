from flask import Blueprint, jsonify, request
from app.modules.auth import auth_required

bp = Blueprint("settings", __name__)

settings_db = {
    "tolerance_minutes": 10,
    "absence_limit_minutes": 30
}


@bp.get("/attendance")
@auth_required()
def get_attendance_settings():
    return jsonify(settings_db), 200


@bp.put("/attendance")
@auth_required("director")
def update_attendance_settings():
    data = request.get_json() or {}
    tolerance = data.get("tolerance_minutes")
    absence_limit = data.get("absence_limit_minutes")

    if tolerance is None or absence_limit is None or tolerance < 0 or absence_limit < 0:
        return jsonify({"error": "Parámetros inválidos"}), 400

    settings_db["tolerance_minutes"] = tolerance
    settings_db["absence_limit_minutes"] = absence_limit

    return jsonify(settings_db), 200