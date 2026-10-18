from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class GestionEscolar(db.Model):
    __tablename__ = "gestiones_escolares"

    id_gestion: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_unidad: Mapped[int] = mapped_column(Integer)
    anio: Mapped[int] = mapped_column(SmallInteger)
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(15))


class Curso(db.Model):
    __tablename__ = "cursos"

    id_curso: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_unidad: Mapped[int] = mapped_column(Integer)
    nivel: Mapped[str] = mapped_column(String(40))
    grado: Mapped[int] = mapped_column(SmallInteger)
    paralelo: Mapped[str] = mapped_column(String(1))
    turno: Mapped[str] = mapped_column(String(15))


class Estudiante(db.Model):
    __tablename__ = "estudiantes"

    id_estudiante: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_usuario: Mapped[int | None] = mapped_column(Integer)
    codigo_estudiante: Mapped[str] = mapped_column(String(25), unique=True)
    nombres: Mapped[str] = mapped_column(String(80))
    apellidos: Mapped[str] = mapped_column(String(100))
    fecha_nacimiento: Mapped[date] = mapped_column(Date)
    genero: Mapped[str | None] = mapped_column(String(20))
    estado: Mapped[str] = mapped_column(String(15))


class Inscripcion(db.Model):
    __tablename__ = "inscripciones"

    id_inscripcion: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_estudiante: Mapped[int] = mapped_column(ForeignKey("estudiantes.id_estudiante"))
    id_curso: Mapped[int] = mapped_column(ForeignKey("cursos.id_curso"))
    id_gestion: Mapped[int] = mapped_column(ForeignKey("gestiones_escolares.id_gestion"))
    fecha_inscripcion: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(15))


class Profesor(db.Model):
    __tablename__ = "profesores"

    id_profesor: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(Integer)
    estado: Mapped[str] = mapped_column(String(15))


class AsignacionDocente(db.Model):
    __tablename__ = "asignaciones_docentes"

    id_asignacion: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_profesor: Mapped[int] = mapped_column(ForeignKey("profesores.id_profesor"))
    id_curso: Mapped[int] = mapped_column(ForeignKey("cursos.id_curso"))
    id_gestion: Mapped[int] = mapped_column(ForeignKey("gestiones_escolares.id_gestion"))


class ObservacionEstudiante(db.Model):
    __tablename__ = "observaciones_estudiante"

    id_observacion: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_estudiante: Mapped[int] = mapped_column(ForeignKey("estudiantes.id_estudiante"))
    registrada_por: Mapped[int] = mapped_column(Integer)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime)
    tipo: Mapped[str] = mapped_column(String(25))
    descripcion: Mapped[str] = mapped_column(Text)
    confidencial: Mapped[bool] = mapped_column(Boolean)
    estado: Mapped[str] = mapped_column(String(15))