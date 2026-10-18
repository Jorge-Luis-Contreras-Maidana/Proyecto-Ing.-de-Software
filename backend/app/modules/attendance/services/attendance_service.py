from datetime import datetime, time
from sqlalchemy import text
from app.extensions import db
from app.modules.attendance.models.attendance import RegistroAsistencia
from app.modules.settings.api.routes import settings_db
from app.modules.qr.services.totp_service import TOTPService

class AttendanceService:
    HORA_INICIO_CLASES = time(8, 0, 0)

    @classmethod
    def registrar_ingreso_qr(cls, id_estudiante: int, codigo_qr: str, secreto_estudiante: str = "JBSWY3DPEHPK3PXP"):
        # 1. Validar QR
        if not TOTPService.verify_code(secreto_estudiante, codigo_qr):
            return {"error": "Código QR expirado o inválido", "codigo": "QR_INVALIDO"}, 400

        ahora = datetime.now()
        hoy = ahora.date()

        # Obtener o simular una sesión de clase para el día de hoy
        res_sesion = db.session.execute(
            text("SELECT id_sesion_clase FROM sesco.sesiones_clase WHERE fecha = :f LIMIT 1"),
            {"f": hoy}
        ).fetchone()

        id_sesion_clase = res_sesion[0] if res_sesion else 1

        # 2. Control de idempotencia / duplicados
        existente = RegistroAsistencia.query.filter_by(
            id_sesion_clase=id_sesion_clase, 
            id_estudiante=id_estudiante
        ).first()

        if existente and existente.hora_ingreso:
            return {
                "mensaje": "Ingreso ya registrado previamente hoy",
                "id_asistencia": existente.id_asistencia,
                "estado": existente.estado,
                "hora_ingreso": existente.hora_ingreso.strftime("%H:%M:%S")
            }, 200

        # 3. Clasificación según tolerancia
        hora_inicio = datetime.combine(hoy, cls.HORA_INICIO_CLASES)
        minutos_diferencia = (ahora - hora_inicio).total_seconds() / 60.0

        tolerancia = settings_db.get("tolerance_minutes", 10)
        limite_falta = settings_db.get("absence_limit_minutes", 30)

        if minutos_diferencia <= tolerancia:
            estado = "presente"
        elif minutos_diferencia <= limite_falta:
            estado = "tarde"
        else:
            estado = "ausente"

        if existente:
            existente.estado = estado
            existente.hora_ingreso = ahora
            existente.metodo_ingreso = "qr"
            nuevo_registro = existente
        else:
            nuevo_registro = RegistroAsistencia(
                id_sesion_clase=id_sesion_clase,
                id_estudiante=id_estudiante,
                hora_ingreso=ahora,
                estado=estado,
                metodo_ingreso="qr"
            )
            db.session.add(nuevo_registro)

        db.session.commit()

        return {
            "mensaje": "Asistencia registrada correctamente",
            "id_asistencia": nuevo_registro.id_asistencia,
            "estado": estado,
            "hora_ingreso": ahora.strftime("%H:%M:%S")
        }, 201