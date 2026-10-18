from datetime import datetime
from app.extensions import db

class RegistroAsistencia(db.Model):
    __tablename__ = "asistencias"
    __table_args__ = (
        db.UniqueConstraint("id_sesion_clase", "id_estudiante", name="uq_sesion_estudiante"),
        {"schema": "sesco"}
    )

    id_asistencia = db.Column(db.BigInteger, primary_key=True)
    id_sesion_clase = db.Column(db.Integer, db.ForeignKey("sesco.sesiones_clase.id_sesion_clase"), nullable=False)
    id_estudiante = db.Column(db.Integer, db.ForeignKey("sesco.estudiantes.id_estudiante"), nullable=False)
    estado = db.Column(db.String(20), nullable=False)  # presente, tarde, ausente, justificada, pendiente
    hora_ingreso = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    metodo_ingreso = db.Column(db.String(15), nullable=True, default="qr")
    registrado_por = db.Column(db.Integer, db.ForeignKey("sesco.usuarios.id_usuario"), nullable=True)
    observacion = db.Column(db.Text, nullable=True)