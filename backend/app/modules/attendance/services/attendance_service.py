"""Reglas de negocio de la asistencia. No usa Flask ni escribe SQL."""
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import select

from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.core.errors.exceptions import InvalidData, NotFound, PermissionDenied
from app.extensions import db
from app.modules.attendance.models.attendance import RegistroAsistencia
from app.modules.attendance.repositories.attendance_repository import AttendanceRepository
from app.modules.attendance.services.attendance_rules import (
    PENDIENTE,
    clasificar,
    minutos_de_retraso,
    resumen,
)
from app.modules.qr.services.qr_service import QRService
from app.modules.settings.services.settings_service import SettingsService
from app.modules.students.models.students import Estudiante

PERSONAL = ("director", "profesor")


@dataclass(frozen=True)
class RegistroResultado:
    id_asistencia: int
    id_sesion_clase: int
    id_estudiante: int
    estado: str
    hora_ingreso: datetime | None
    ya_registrado: bool
    minutos_retraso: float


class AttendanceService:
    def __init__(self, repo=None, qr=None, settings=None):
        self.repo = repo or AttendanceRepository()
        self.qr = qr or QRService()
        self.settings = settings or SettingsService()

    # ---------- resolución de la sesión ----------
    def _resolver_sesion(self, id_estudiante: int, id_sesion_clase: int | None, ahora: datetime):
        """Elige la sesión de clase a la que se registra el ingreso.

        Prioridad: la sesión indicada por el personal, la que está en curso en
        este momento, la más reciente que ya empezó y, en último caso, la
        próxima que empieza.
        """
        hoy = ahora.date()
        if id_sesion_clase is not None:
            sesion = self.repo.get_session(id_sesion_clase)
            if sesion is None:
                raise NotFound("No se encontró la sesión de clase.", "Verifique la sesión o genere el horario del día.")
            if sesion.fecha != hoy:
                raise InvalidData(
                    "La sesión de clase no es de hoy.",
                    "Seleccione la sesión de la fecha que está registrando.",
                )
            return sesion

        candidatas = self.repo.sessions_for_student(id_estudiante, hoy)
        if not candidatas:
            raise NotFound(
                "Hoy no hay ninguna clase programada para este estudiante.",
                "Genere el horario del día o registre la asistencia manualmente.",
            )

        hora_actual = ahora.time()
        en_curso = [s for s in candidatas if s.hora_inicio_prevista <= hora_actual <= s.hora_fin_prevista]
        if en_curso:
            return en_curso[0]
        ya_empezadas = [s for s in candidatas if s.hora_inicio_prevista <= hora_actual]
        if ya_empezadas:
            return ya_empezadas[-1]
        return candidatas[0]

    # ---------- registro por QR ----------
    def registrar_por_qr(
        self,
        principal,
        id_estudiante: int,
        codigo: str,
        id_sesion_clase: int | None = None,
    ) -> RegistroResultado:
        """Registra el ingreso de un estudiante validando su credencial QR.

        La clasificación usa la hora de inicio prevista de la sesión y los
        parámetros vigentes de la unidad educativa.
        """
        estudiante = db.session.get(Estudiante, id_estudiante)
        if estudiante is None:
            raise NotFound("No se encontró el estudiante.", "Verifique el estudiante o regrese al inicio.")
        if estudiante.estado != "activo":
            raise InvalidData("El estudiante no está activo.", "No se puede registrar la asistencia de un estudiante retirado.")

        ahora = clock.now()
        sesion = self._resolver_sesion(id_estudiante, id_sesion_clase, ahora)

        # La credencial es del propio estudiante: el QR de otro no sirve.
        validacion = self.qr.verificar(principal, id_estudiante, codigo)

        parametros = self.settings.get()
        estado = clasificar(
            sesion.hora_inicio_prevista,
            ahora,
            parametros.tolerancia_ingreso_min,
            parametros.limite_tardanza_min,
        )

        existente = self.repo.get_asistencia(sesion.id_sesion_clase, id_estudiante)
        ya_registrado = existente is not None and existente.hora_ingreso is not None

        if ya_registrado:
            # El ingreso ya estaba registrado: no se modifica nada. La lectura
            # de QR tampoco, porque la tabla admite una sola por asistencia.
            return RegistroResultado(
                id_asistencia=existente.id_asistencia,
                id_sesion_clase=sesion.id_sesion_clase,
                id_estudiante=id_estudiante,
                estado=existente.estado,
                hora_ingreso=existente.hora_ingreso,
                ya_registrado=True,
                minutos_retraso=minutos_de_retraso(sesion.hora_inicio_prevista, ahora),
            )

        with unit_of_work():
            if existente is None:
                asistencia = self.repo.add_asistencia(
                    RegistroAsistencia(
                        id_sesion_clase=sesion.id_sesion_clase,
                        id_estudiante=id_estudiante,
                        estado=estado,
                        hora_ingreso=ahora,
                        metodo_ingreso="qr",
                        registrado_por=principal.id_usuario,
                    )
                )
            else:
                asistencia = existente
                asistencia.estado = estado
                asistencia.hora_ingreso = ahora
                asistencia.metodo_ingreso = "qr"
                asistencia.registrado_por = principal.id_usuario
            if not self.qr.tiene_lectura(asistencia.id_asistencia):
                self.qr.registrar_lectura(
                    id_credencial=validacion["id_credencial"],
                    ventana=validacion["ventana_totp"],
                    id_asistencia=asistencia.id_asistencia,
                    resultado="aceptado",
                )

        return RegistroResultado(
            id_asistencia=asistencia.id_asistencia,
            id_sesion_clase=sesion.id_sesion_clase,
            id_estudiante=id_estudiante,
            estado=estado,
            hora_ingreso=ahora,
            ya_registrado=False,
            minutos_retraso=minutos_de_retraso(sesion.hora_inicio_prevista, ahora),
        )

    # ---------- registro manual ----------
    def marcar_manual(self, principal, id_sesion_clase: int, id_estudiante: int, estado: str, observacion: str | None = None):
        """El personal registra la asistencia sin escanear el QR."""
        sesion = self.repo.get_session(id_sesion_clase)
        if sesion is None:
            raise NotFound("No se encontró la sesión de clase.", "Verifique la sesión o genere el horario del día.")
        estudiante = db.session.get(Estudiante, id_estudiante)
        if estudiante is None:
            raise NotFound("No se encontró el estudiante.", "Verifique el estudiante o regrese al inicio.")

        with unit_of_work():
            asistencia = self.repo.get_asistencia(id_sesion_clase, id_estudiante)
            if asistencia is None:
                asistencia = self.repo.add_asistencia(
                    RegistroAsistencia(
                        id_sesion_clase=id_sesion_clase,
                        id_estudiante=id_estudiante,
                        estado=estado,
                        hora_ingreso=clock.now() if estado in ("presente", "tarde") else None,
                        metodo_ingreso="manual",
                        registrado_por=principal.id_usuario,
                        observacion=observacion,
                    )
                )
            else:
                asistencia.estado = estado
                asistencia.metodo_ingreso = "manual"
                asistencia.registrado_por = principal.id_usuario
                if observacion is not None:
                    asistencia.observacion = observacion
        return asistencia

    # ---------- consultas ----------
    def _es_personal(self, principal) -> bool:
        return bool(set(principal.roles) & set(PERSONAL))

    def _curso_visible(self, principal, id_curso: int) -> bool:
        if "director" in principal.roles:
            return True
        if "profesor" in principal.roles:
            return id_curso in self.repo.professor_courses(principal.id_usuario)
        return False

    def hoy(self, principal, fecha: date | None = None) -> list[dict]:
        """Sesiones de la fecha con el conteo de asistencia de cada una."""
        dia = fecha or clock.now().date()
        if self._es_personal(principal):
            if "director" in principal.roles:
                filas = self.repo.sessions_for_date(dia)
            else:
                cursos = self.repo.professor_courses(principal.id_usuario)
                filas = [f for f in self.repo.sessions_for_date(dia) if f[1].id_curso in cursos]
        else:
            raise PermissionDenied()
        return [self._session_payload(f, dia) for f in filas]

    def _session_payload(self, fila, dia: date) -> dict:
        sesion, asignacion, curso = fila
        conteos = self.repo.count_by_state(sesion.id_sesion_clase)
        return {
            "id_sesion_clase": sesion.id_sesion_clase,
            "fecha": dia.isoformat(),
            "hora_inicio_prevista": sesion.hora_inicio_prevista.strftime("%H:%M"),
            "hora_fin_prevista": sesion.hora_fin_prevista.strftime("%H:%M"),
            "estado": sesion.estado,
            "id_curso": curso.id_curso,
            "curso": f"{curso.nivel} {curso.grado}{curso.paralelo}",
            "turno": curso.turno,
            "id_asignacion": asignacion.id_asignacion,
            "asistencia": resumen(conteos),
        }

    def sesion(self, principal, id_sesion_clase: int) -> dict:
        """Detalle de una sesión: qué estudiantes tiene y en qué estado están."""
        sesion = self.repo.get_session(id_sesion_clase)
        if sesion is None:
            raise NotFound("No se encontró la sesión de clase.", "Verifique la sesión o genere el horario del día.")
        from app.modules.attendance.repositories.attendance_repository import AttendanceRepository  # noqa: F401
        from app.modules.students.models.students import AsignacionDocente

        asignacion = db.session.get(AsignacionDocente, sesion.id_asignacion)
        if asignacion is None:
            raise NotFound("No se encontró la asignación docente de la sesión.", "Verifique la sesión.")
        if not self._curso_visible(principal, asignacion.id_curso):
            raise PermissionDenied(
                "No tiene permiso para ver esta clase.",
                "La clase pertenece a un curso en el que no imparte.",
            )

        filas = self.repo.students_of_session(id_sesion_clase)
        estudiantes = []
        for id_estudiante, asistencia in filas:
            est = db.session.get(Estudiante, id_estudiante)
            if est is None:
                continue
            estudiantes.append(
                {
                    "id_estudiante": id_estudiante,
                    "nombres": est.nombres,
                    "apellidos": est.apellidos,
                    "codigo_estudiante": est.codigo_estudiante,
                    "estado": asistencia.estado if asistencia else PENDIENTE,
                    "hora_ingreso": asistencia.hora_ingreso.isoformat(timespec="seconds") if asistencia and asistencia.hora_ingreso else None,
                    "metodo_ingreso": asistencia.metodo_ingreso if asistencia else None,
                }
            )
        datos = self._session_payload((sesion, asignacion, self._curso_de(asignacion.id_curso)), sesion.fecha)
        datos["estudiantes"] = estudiantes
        return datos

    def _curso_de(self, id_curso: int):
        from app.modules.students.models.students import Curso

        return db.session.get(Curso, id_curso)

    def historial(self, principal, id_estudiante: int, desde: date | None = None, hasta: date | None = None) -> list[dict]:
        """Historial de asistencia de un estudiante."""
        if "estudiante" in principal.roles:
            propio = db.session.execute(
                select(Estudiante.id_estudiante).where(Estudiante.id_usuario == principal.id_usuario)
            ).scalar_one_or_none()
            if propio != id_estudiante:
                raise NotFound("No se encontró el estudiante.", "Verifique el estudiante o regrese al inicio.")
        elif "tutor" in principal.roles and not self._es_personal(principal):
            if not self._tutor_vinculado(principal.id_usuario, id_estudiante):
                raise NotFound("No se encontró el estudiante.", "Verifique el estudiante o regrese al inicio.")
        return [
            {
                "id_asistencia": asistencia.id_asistencia,
                "id_sesion_clase": sesion.id_sesion_clase,
                "fecha": sesion.fecha.isoformat(),
                "hora_inicio_prevista": sesion.hora_inicio_prevista.strftime("%H:%M"),
                "estado": asistencia.estado,
                "hora_ingreso": asistencia.hora_ingreso.isoformat(timespec="seconds") if asistencia.hora_ingreso else None,
                "metodo_ingreso": asistencia.metodo_ingreso,
            }
            for asistencia, sesion in self.repo.attendance_history(id_estudiante, desde, hasta)
        ]

    def _tutor_vinculado(self, id_usuario: int, id_estudiante: int) -> bool:
        from app.modules.students.models.guardian_link import EstudianteTutor, Tutor

        stmt = (
            select(EstudianteTutor.id_estudiante)
            .join(Tutor, Tutor.id_tutor == EstudianteTutor.id_tutor)
            .where(Tutor.id_usuario == id_usuario, EstudianteTutor.confirmado.is_(True))
        )
        return id_estudiante in db.session.execute(stmt).scalars().all()
