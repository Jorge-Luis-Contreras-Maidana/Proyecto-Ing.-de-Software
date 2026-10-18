from datetime import datetime
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.modules.auth import auth_required
from app.modules.justifications.models.justification import JustificacionAusencia

bp = Blueprint("justifications", __name__)

@bp.get("")
@auth_required("director", "profesor", "tutor")
def listar_justificaciones():
    items = JustificacionAusencia.query.order_by(JustificacionAusencia.solicitada_en.desc()).all()
    res = [
        {
            "id_justificacion": j.id_justificacion,
            "id_estudiante": j.id_estudiante,
            "fecha_inicio": j.fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_fin": j.fecha_fin.strftime("%Y-%m-%d"),
            "motivo": j.motivo_declarado,
            "estado": j.estado
        }
        for j in items
    ]
    return jsonify({"items": res, "total": len(res)}), 200

@bp.post("")
@auth_required("tutor")
def crear_justificacion():
    data = request.get_json() or {}
    nueva = JustificacionAusencia(
        id_estudiante=data.get("id_estudiante"),
        id_tutor=data.get("id_tutor", 1),
        fecha_inicio=datetime.strptime(data.get("fecha_inicio"), "%Y-%m-%d").date(),
        fecha_fin=datetime.strptime(data.get("fecha_fin"), "%Y-%m-%d").date(),
        motivo_declarado=data.get("motivo", "")
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify({"mensaje": "Justificación registrada", "id_justificacion": nueva.id_justificacion}), 201

@bp.put("/<int:id_justificacion>/estado")
@auth_required("director")
def cambiar_estado_justificacion(id_justificacion: int):
    data = request.get_json() or {}
    j = JustificacionAusencia.query.get_or_404(id_justificacion)
    j.estado = data.get("estado", j.estado)
    j.revisada_en = datetime.utcnow()
    j.comentario_revision = data.get("comentario")
    db.session.commit()
    return jsonify({"mensaje": "Estado actualizado correctamente"}), 200