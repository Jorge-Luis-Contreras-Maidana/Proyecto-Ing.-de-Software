from app.core import clock
from app.extensions import db


class JustificacionAusencia(db.Model):
    __tablename__ = "justificaciones_ausencia"
    __table_args__ = {"schema": "sesco"}

    id_justificacion = db.Column(db.Integer, primary_key=True)
    id_estudiante = db.Column(db.Integer, db.ForeignKey("sesco.estudiantes.id_estudiante"), nullable=False)
    id_tutor = db.Column(db.Integer, db.ForeignKey("sesco.tutores.id_tutor"), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    motivo_declarado = db.Column(db.Text, nullable=False)
    documento_referencia = db.Column(db.Text, nullable=True)
    solicitada_en = db.Column(db.DateTime, nullable=False, default=clock.now)
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    revisada_por = db.Column(db.Integer, db.ForeignKey("sesco.usuarios.id_usuario"), nullable=True)
    revisada_en = db.Column(db.DateTime, nullable=True)
    comentario_revision = db.Column(db.Text, nullable=True)
