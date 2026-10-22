from datetime import date, datetime, time

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class SesionClase(db.Model):
    """Clase programada: es el contexto contra el que se registra la asistencia."""

    __tablename__ = "sesiones_clase"

    id_sesion_clase: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_asignacion: Mapped[int] = mapped_column(ForeignKey("asignaciones_docentes.id_asignacion"))
    fecha: Mapped[date] = mapped_column(Date)
    hora_inicio_prevista: Mapped[time] = mapped_column(Time)
    hora_apertura_real: Mapped[datetime | None] = mapped_column(DateTime)
    hora_cierre_real: Mapped[datetime | None] = mapped_column(DateTime)
    abierta_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"))
    hora_fin_prevista: Mapped[time] = mapped_column(Time)
    estado: Mapped[str] = mapped_column(String(20))
    observacion: Mapped[str | None] = mapped_column(Text)


class RegistroAsistencia(db.Model):
    """Asistencia de un estudiante a una sesión de clase."""

    __tablename__ = "asistencias"
    __table_args__ = (
        db.UniqueConstraint("id_sesion_clase", "id_estudiante", name="uq_asistencia_sesion_estudiante"),
    )

    id_asistencia: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_sesion_clase: Mapped[int] = mapped_column(ForeignKey("sesiones_clase.id_sesion_clase"))
    id_estudiante: Mapped[int] = mapped_column(ForeignKey("estudiantes.id_estudiante"))
    estado: Mapped[str] = mapped_column(String(20))
    hora_ingreso: Mapped[datetime | None] = mapped_column(DateTime)
    hora_salida_aula: Mapped[datetime | None] = mapped_column(DateTime)
    metodo_ingreso: Mapped[str | None] = mapped_column(String(15))
    registrado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"))
    observacion: Mapped[str | None] = mapped_column(Text)
    id_justificacion: Mapped[int | None] = mapped_column(ForeignKey("justificaciones_ausencia.id_justificacion"))


class AvisoInasistenciaDocente(db.Model):
    """Aviso de que un docente no asistió a su clase."""

    __tablename__ = "avisos_inasistencia_docente"

    id_aviso_docente: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_profesor: Mapped[int] = mapped_column(ForeignKey("profesores.id_profesor"))
    id_sesion_clase: Mapped[int | None] = mapped_column(ForeignKey("sesiones_clase.id_sesion_clase"))
    fecha_afectada: Mapped[date] = mapped_column(Date)
    motivo: Mapped[str] = mapped_column(Text)
    enviado_en: Mapped[datetime] = mapped_column(DateTime)
    estado: Mapped[str] = mapped_column(String(20))
    revisado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"))
    revisado_en: Mapped[datetime | None] = mapped_column(DateTime)
    decision: Mapped[str | None] = mapped_column(Text)


class AutorizacionSalida(db.Model):
    """Autorización de salida anticipada de la unidad educativa."""

    __tablename__ = "autorizaciones_salida"

    id_autorizacion: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_curso: Mapped[int] = mapped_column(ForeignKey("cursos.id_curso"))
    id_gestion: Mapped[int] = mapped_column(ForeignKey("gestiones_escolares.id_gestion"))
    id_aviso_docente: Mapped[int | None] = mapped_column(ForeignKey("avisos_inasistencia_docente.id_aviso_docente"))
    solicitada_por: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"))
    autorizada_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"))
    fecha_salida: Mapped[date] = mapped_column(Date)
    hora_salida_prevista: Mapped[time] = mapped_column(Time)
    motivo: Mapped[str] = mapped_column(Text)
    solicitada_en: Mapped[datetime] = mapped_column(DateTime)
    resuelta_en: Mapped[datetime | None] = mapped_column(DateTime)
    estado: Mapped[str] = mapped_column(String(20))
    observacion: Mapped[str | None] = mapped_column(Text)


class RegistroSalida(db.Model):
    """Salida efectiva de un estudiante de la unidad educativa."""

    __tablename__ = "registros_salida"

    id_registro_salida: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_estudiante: Mapped[int] = mapped_column(ForeignKey("estudiantes.id_estudiante"))
    id_gestion: Mapped[int] = mapped_column(ForeignKey("gestiones_escolares.id_gestion"))
    id_curso: Mapped[int] = mapped_column(ForeignKey("cursos.id_curso"))
    id_autorizacion: Mapped[int | None] = mapped_column(ForeignKey("autorizaciones_salida.id_autorizacion"))
    fecha_salida: Mapped[date] = mapped_column(Date)
    hora_salida_real: Mapped[datetime | None] = mapped_column(DateTime)
    metodo_registro: Mapped[str] = mapped_column(String(15))
    estado_verificacion: Mapped[str] = mapped_column(String(20))
    registrado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"))
    observacion: Mapped[str | None] = mapped_column(Text)
