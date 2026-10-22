from flask import Blueprint

from app.extensions import db
from app.modules.auth import auth_required, current_principal
from app.modules.qr.api.schemas import QRVerifyRequest, parse_json, qr_payload
from app.modules.qr.services.qr_service import QRService
from app.modules.students.models.students import Estudiante

bp = Blueprint("qr", __name__)


def _service() -> QRService:
    return QRService()


@bp.get("/me/code")
@auth_required()
def get_my_qr_code():
    """Credencial del estudiante que inició sesión."""
    id_estudiante = QRService._id_estudiante_del_usuario(current_principal().id_usuario)
    if id_estudiante is None:
        return {
            "error": {
                "codigo": "no_encontrado",
                "mensaje": "Su cuenta no está vinculada a un estudiante.",
                "accion": "Comuníquese con la dirección de la unidad educativa.",
            }
        }, 404
    return qr_payload(_service().codigo_del_estudiante(current_principal(), id_estudiante))


@bp.get("/student/<int:id_estudiante>")
@auth_required("director", "profesor")
def get_student_qr_info(id_estudiante: int):
    """Credencial y datos básicos de un estudiante, para el personal."""
    estudiante = db.session.get(Estudiante, id_estudiante)
    if estudiante is None:
        return {
            "error": {
                "codigo": "no_encontrado",
                "mensaje": "No se encontró el estudiante.",
                "accion": "Verifique el estudiante o regrese al inicio.",
            }
        }, 404
    resultado = _service().codigo_del_estudiante(current_principal(), id_estudiante)
    return {
        "id_estudiante": estudiante.id_estudiante,
        "nombres": estudiante.nombres,
        "apellidos": estudiante.apellidos,
        "codigo_estudiante": estudiante.codigo_estudiante,
        "estado": estudiante.estado,
        "credencial_activa": True,
        "id_credencial": resultado.id_credencial,
        "codigo": resultado.code,
        "expira_en_segundos": resultado.expires_in,
        "imagen": f"data:image/png;base64,{resultado.imagen_base64}",
    }


@bp.post("/verify")
@auth_required("profesor", "director")
def verify_qr():
    """Valida un código QR sin registrar la asistencia."""
    data = parse_json(QRVerifyRequest)
    _service().verificar(current_principal(), data.id_estudiante, data.codigo)
    return {"valido": True, "id_estudiante": data.id_estudiante}


@bp.post("/student/<int:id_estudiante>/renovar")
@auth_required("director")
def renew_student_qr(id_estudiante: int):
    """Emite una credencial nueva, revocando la anterior."""
    estudiante = db.session.get(Estudiante, id_estudiante)
    if estudiante is None:
        return {
            "error": {
                "codigo": "no_encontrado",
                "mensaje": "No se encontró el estudiante.",
                "accion": "Verifique el estudiante o regrese al inicio.",
            }
        }, 404
    return qr_payload(_service().renovar_credencial(current_principal(), id_estudiante))
