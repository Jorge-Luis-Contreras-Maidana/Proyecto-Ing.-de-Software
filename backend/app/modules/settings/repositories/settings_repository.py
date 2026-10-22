from sqlalchemy import select

from app.extensions import db
from app.modules.settings.models.settings import ConfiguracionAsistencia


class SettingsRepository:
    def get_by_unidad(self, id_unidad: int) -> ConfiguracionAsistencia | None:
        stmt = select(ConfiguracionAsistencia).where(ConfiguracionAsistencia.id_unidad == id_unidad)
        return db.session.execute(stmt).scalar_one_or_none()

    def first(self) -> ConfiguracionAsistencia | None:
        stmt = select(ConfiguracionAsistencia).order_by(ConfiguracionAsistencia.id_configuracion).limit(1)
        return db.session.execute(stmt).scalar_one_or_none()
