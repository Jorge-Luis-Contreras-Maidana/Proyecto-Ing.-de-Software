from flask import Blueprint

from app.modules.auth import auth_required, current_principal
from app.modules.settings.api.schemas import SettingsUpdate, parse_json, settings_payload
from app.modules.settings.services.settings_service import SettingsService

bp = Blueprint("settings", __name__)


def _service() -> SettingsService:
    return SettingsService()


@bp.get("/attendance")
@auth_required()
def get_attendance_settings():
    return settings_payload(_service().get())


@bp.put("/attendance")
@auth_required("director")
def update_attendance_settings():
    data = parse_json(SettingsUpdate)
    return settings_payload(_service().update(current_principal(), data.model_dump(exclude_unset=True)))
