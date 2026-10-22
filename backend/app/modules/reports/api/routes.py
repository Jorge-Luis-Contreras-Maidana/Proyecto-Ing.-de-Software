"""Rutas del módulo de reportes de asistencia."""
from flask import Blueprint

from app.core.http import parse_query
from app.modules.auth import auth_required, current_principal
from app.modules.reports.api.schemas import ReporteAsistenciaQuery, ReporteDiarioQuery
from app.modules.reports.services.reports_service import ReportsService

bp = Blueprint("reports", __name__)


def _service() -> ReportsService:
    return ReportsService()


@bp.get("/resumen")
@auth_required("director", "profesor")
def resumen_general():
    """Totales de la gestión activa y desglose por curso."""
    return _service().resumen(current_principal())


@bp.get("/asistencia")
@auth_required("director", "profesor")
def reporte_asistencia():
    """Asistencia por estudiante con sus conteos y porcentaje."""
    f = parse_query(ReporteAsistenciaQuery)
    filas = _service().asistencia(
        current_principal(), f.desde, f.hasta, f.id_curso, f.id_estudiante
    )
    return {"items": filas, "total": len(filas)}


@bp.get("/estudiante/<int:id_estudiante>")
@auth_required("director", "profesor", "tutor")
def reporte_estudiante(id_estudiante: int):
    """Detalle del reporte de un estudiante. El tutor solo de sus hijos."""
    return _service().estudiante(current_principal(), id_estudiante)


@bp.get("/diario")
@auth_required("director", "profesor")
def reporte_diario():
    """Resumen de un día (vista v_asistencia_diaria)."""
    f = parse_query(ReporteDiarioQuery)
    items = _service().diario(current_principal(), f.fecha)
    return {"items": items, "total": len(items)}
