"""Reglas de los reportes de asistencia. No usa Flask ni escribe SQL."""
from datetime import date

from app.core import clock
from app.core.errors.exceptions import InvalidData, NotFound
from app.modules.reports.repositories.reports_repository import ReportsRepository
from app.modules.reports.services.report_builder import (
    bloque_conteos,
    bloque_curso_general,
    bloque_lecturas,
    bloque_por_curso,
    bloque_por_mes,
    fila_asistencia,
    fila_diaria,
    resumen_general,
)
from app.modules.students.models.students import Estudiante

# Últimas lecturas que se muestran en el detalle de un estudiante.
ULTIMAS_LECTURAS = 10


class ReportsService:
    def __init__(self, repo=None):
        self.repo = repo or ReportsRepository()

    # ---------- apoyo ----------
    def _gestion(self):
        gestion = self.repo.active_gestion()
        if gestion is None:
            raise InvalidData(
                "No hay una gestión escolar activa.",
                "Active una gestión antes de consultar los reportes.",
            )
        return gestion

    def _access(self, principal, columna):
        """Condición de visibilidad según el rol del usuario (RD-02.1)."""
        gestion = self.repo.active_gestion()
        id_gestion = gestion.id_gestion if gestion else None
        return self.repo.access_condition(columna, principal.roles, principal.id_usuario, id_gestion)

    def _cursos(self) -> dict[int, dict]:
        return {
            curso.id_curso: {
                "id_curso": curso.id_curso,
                "nivel": curso.nivel,
                "grado": curso.grado,
                "paralelo": curso.paralelo,
                "turno": curso.turno,
            }
            for curso in self.repo.cursos()
        }

    # ---------- resumen general ----------
    def resumen(self, principal) -> dict:
        """Totales de la gestión activa y desglose por curso."""
        gestion = self._gestion()
        resumen = self.repo.resumen(gestion.id_gestion)
        cursos = self._cursos()
        por_curso = [
            bloque_curso_general(conteos, cursos.get(conteos["id_curso"]))
            for conteos in self.repo.resumen_por_curso(gestion.id_gestion)
        ]
        return resumen_general(resumen, por_curso)

    # ---------- asistencia por estudiante ----------
    def asistencia(
        self,
        principal,
        desde: date | None = None,
        hasta: date | None = None,
        id_curso: int | None = None,
        id_estudiante: int | None = None,
    ) -> list[dict]:
        """Una fila por estudiante con sus conteos y porcentaje de asistencia."""
        gestion = self._gestion()
        if desde is not None and hasta is not None and desde > hasta:
            raise InvalidData(
                "La fecha inicial no puede ser posterior a la final.",
                "Corrija el rango de fechas e intente nuevamente.",
            )
        if id_curso is not None and self.repo.get_curso(id_curso) is None:
            raise NotFound("El curso indicado no existe.", "Elija un curso de la lista.")

        access = self._access(principal, Estudiante.id_estudiante)
        filas = self.repo.asistencia_por_estudiante(
            gestion.id_gestion, desde, hasta, id_curso, id_estudiante, access
        )
        cursos = self.repo.cursos_por_estudiante(gestion.id_gestion)
        return [fila_asistencia(fila, cursos.get(fila["id_estudiante"])) for fila in filas]

    # ---------- detalle de un estudiante ----------
    def estudiante(self, principal, id_estudiante: int) -> dict:
        """Detalle del reporte de un estudiante."""
        gestion = self._gestion()
        estudiante = self.repo.get_estudiante(id_estudiante)
        if estudiante is None:
            raise NotFound("No se encontró el estudiante.", "Verifique el estudiante o regrese al inicio.")

        access = self._access(principal, Estudiante.id_estudiante)
        if access is not None:
            visible = self.repo.estudiante_visible(id_estudiante, access)
            if not visible:
                # No se revela si el estudiante existe o no (RD-02.1).
                raise NotFound("No se encontró el estudiante.", "Verifique el estudiante o regrese al inicio.")

        cursos = self._cursos()
        curso_estudiante = self.repo.cursos_por_estudiante(gestion.id_gestion).get(id_estudiante)
        datos_estudiante = {
            "id_estudiante": estudiante.id_estudiante,
            "codigo_estudiante": estudiante.codigo_estudiante,
            "nombres": estudiante.nombres,
            "apellidos": estudiante.apellidos,
            "fecha_nacimiento": estudiante.fecha_nacimiento.isoformat(),
            "genero": estudiante.genero,
            "estado": estudiante.estado,
            "curso": curso_estudiante,
        }

        por_curso = bloque_por_curso(self.repo.conteos_por_curso(id_estudiante, gestion.id_gestion), cursos)
        por_mes = bloque_por_mes(self.repo.conteos_por_mes(id_estudiante, gestion.id_gestion))
        lecturas = bloque_lecturas(
            self.repo.ultimas_lecturas(id_estudiante, ULTIMAS_LECTURAS), cursos
        )

        resumen = bloque_conteos(
            {
                "total_clases": sum(bloque["total_clases"] for bloque in por_curso),
                "presentes": sum(bloque["presentes"] for bloque in por_curso),
                "tardanzas": sum(bloque["tardanzas"] for bloque in por_curso),
                "ausencias": sum(bloque["ausencias"] for bloque in por_curso),
                "justificadas": sum(bloque["justificadas"] for bloque in por_curso),
                "pendientes": sum(bloque["pendientes"] for bloque in por_curso),
            }
        )
        return {
            "estudiante": datos_estudiante,
            "resumen": resumen,
            "por_curso": por_curso,
            "por_mes": por_mes,
            "ultimas_lecturas": lecturas,
        }

    # ---------- reporte diario ----------
    def diario(self, principal, fecha: date | None = None) -> list[dict]:
        """Resumen del día leído de la vista v_asistencia_diaria."""
        dia = fecha or clock.now().date()
        filas = self.repo.diario(dia)
        access = self._access(principal, Estudiante.id_estudiante)
        if access is not None:
            visibles = {
                estudiante_id
                for (estudiante_id,) in self.repo.ids_visibles(access)
            }
            filas = [fila for fila in filas if fila["id_estudiante"] in visibles]
        return [fila_diaria(fila) for fila in filas]
