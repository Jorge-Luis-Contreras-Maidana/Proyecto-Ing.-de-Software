"""Generación del horario de clases.

Las clases siguen la distribución de la unidad educativa: turno de la mañana a
las 08:00 y turno de la tarde a las 14:00, con 50 minutos entre materias y 45
de duración. Solo se crean días lectivos de lunes a viernes.
"""
from datetime import date, datetime, time, timedelta

from sqlalchemy import select

from app.extensions import db
from app.modules.attendance.models.attendance import RegistroAsistencia, SesionClase
from app.modules.students.models.students import (
    AsignacionDocente,
    Curso,
    GestionEscolar,
    Inscripcion,
)

DURACION_MINUTOS = 45
INICIO_MANANA = time(8, 0)
INICIO_TARDE = time(14, 0)
MINUTOS_POR_MATERIA = 50


def dias_lectivos(desde: date, cantidad: int):
    """Días de lunes a viernes a partir de 'desde'."""
    dia = desde
    while dia.weekday() >= 5:  # salta sábado y domingo
        dia += timedelta(days=1)
    for _ in range(cantidad):
        yield dia
        dia += timedelta(days=1)
        while dia.weekday() >= 5:
            dia += timedelta(days=1)


class ScheduleService:
    def gestion_activa(self) -> GestionEscolar | None:
        stmt = (
            select(GestionEscolar)
            .where(GestionEscolar.estado == "activa")
            .order_by(GestionEscolar.anio.desc())
            .limit(1)
        )
        return db.session.execute(stmt).scalars().first()

    def generar(self, desde: date, dias: int, crear_asistencias: bool = True) -> dict:
        """Crea las sesiones de clase del período indicado. Es idempotente."""
        gestion = self.gestion_activa()
        if gestion is None:
            raise RuntimeError("No hay una gestión escolar activa.")

        asignaciones = db.session.execute(
            select(AsignacionDocente).where(AsignacionDocente.id_gestion == gestion.id_gestion)
        ).scalars().all()
        cursos = {c.id_curso: c for c in db.session.execute(select(Curso)).scalars().all()}

        inscritos_por_curso: dict[int, list[int]] = {}
        if crear_asistencias:
            for curso_id, id_estudiante in db.session.execute(
                select(Inscripcion.id_curso, Inscripcion.id_estudiante).where(
                    Inscripcion.id_gestion == gestion.id_gestion,
                    Inscripcion.estado == "inscrito",
                )
            ).all():
                inscritos_por_curso.setdefault(curso_id, []).append(id_estudiante)

        existentes = {
            (s.id_asignacion, s.fecha, s.hora_inicio_prevista): s
            for s in db.session.execute(
                select(SesionClase).where(SesionClase.fecha >= desde)
            ).scalars().all()
        }

        creadas = 0
        for dia in dias_lectivos(desde, dias):
            for asignacion in asignaciones:
                curso = cursos.get(asignacion.id_curso)
                if curso is None:
                    continue
                base = INICIO_MANANA if curso.turno == "manana" else INICIO_TARDE
                inicio = (
                    datetime.combine(dia, base)
                    + timedelta(minutes=(asignacion.id_materia - 1) * MINUTOS_POR_MATERIA)
                ).time()
                fin = (datetime.combine(dia, inicio) + timedelta(minutes=DURACION_MINUTOS)).time()

                clave = (asignacion.id_asignacion, dia, inicio)
                sesion = existentes.get(clave)
                if sesion is None:
                    sesion = SesionClase(
                        id_asignacion=asignacion.id_asignacion,
                        fecha=dia,
                        hora_inicio_prevista=inicio,
                        hora_fin_prevista=fin,
                        estado="programada",
                    )
                    db.session.add(sesion)
                    db.session.flush()
                    existentes[clave] = sesion
                    creadas += 1

                for id_estudiante in inscritos_por_curso.get(asignacion.id_curso, []):
                    ya_esta = db.session.execute(
                        select(RegistroAsistencia.id_asistencia).where(
                            RegistroAsistencia.id_sesion_clase == sesion.id_sesion_clase,
                            RegistroAsistencia.id_estudiante == id_estudiante,
                        )
                    ).scalar_one_or_none()
                    if ya_esta is None:
                        db.session.add(
                            RegistroAsistencia(
                                id_sesion_clase=sesion.id_sesion_clase,
                                id_estudiante=id_estudiante,
                                estado="pendiente",
                                metodo_ingreso="no_aplica",
                            )
                        )
        db.session.commit()
        return {"sesiones_creadas": creadas, "desde": desde, "dias": dias}

    def asegurar_hoy(self) -> int:
        """Garantiza que exista el horario de hoy. Devuelve cuántas sesiones creó."""
        from app.core import clock

        resultado = self.generar(clock.now().date(), 1, crear_asistencias=True)
        return resultado["sesiones_creadas"]
