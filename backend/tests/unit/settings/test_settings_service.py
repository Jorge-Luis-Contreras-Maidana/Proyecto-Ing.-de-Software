"""Parámetros de la configuración de asistencia."""
from app.core.errors.exceptions import NotFound
from app.modules.settings.services.settings_service import DEFAULTS, SettingsService


def test_los_valores_por_defecto_estan_definidos():
    assert DEFAULTS["tolerancia_ingreso_min"] == 5
    assert DEFAULTS["limite_tardanza_min"] == 15


def test_los_rangos_estan_definidos_para_cada_campo():
    from app.modules.settings.services.settings_service import RANGOS

    assert set(RANGOS) == set(DEFAULTS)


def test_leer_la_configuracion_devuelve_los_parametros_de_la_base(app):
    with app.app_context():
        config = SettingsService().get()
        assert config.id_configuracion > 0
        assert config.tolerancia_ingreso_min >= 0
        assert config.limite_tardanza_min >= 1


def test_actualizar_la_configuracion_persiste(app):
    with app.app_context():
        servicio = SettingsService()
        anterior = servicio.get()
        nuevo = servicio.update(_principal(), {"tolerancia_ingreso_min": 7})
        assert nuevo.tolerancia_ingreso_min == 7
        # Y sigue guardada.
        assert SettingsService().get().tolerancia_ingreso_min == 7
        servicio.update(_principal(), {"tolerancia_ingreso_min": anterior.tolerancia_ingreso_min})


def test_actualizar_sin_configuracion_da_error(app):
    from app.modules.settings.repositories.settings_repository import SettingsRepository

    with app.app_context():
        servicio = SettingsService(repo=SettingsRepository())
        servicio.repo.first = lambda: None
        servicio.repo.get_by_unidad = lambda id_unidad: None
        try:
            servicio.update(_principal(), {"tolerancia_ingreso_min": 7})
        except NotFound:
            return
    raise AssertionError("Debía lanzar NotFound.")


def _principal():
    from app.core.security.rbac import Principal

    return Principal(
        id_usuario=1,
        id_sesion=1,
        nombre_usuario="directora.mquispe",
        nombres="María Elena",
        apellidos="Quispe Rojas",
        roles=("director",),
    )
