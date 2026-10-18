from sqlalchemy import select

from app.extensions import db
from app.modules.auth.models.auth import SesionUsuario, Usuario


class UsuarioRepository:
    def get_by_nombre_usuario(self, nombre_usuario: str) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.nombre_usuario == nombre_usuario)
        return db.session.execute(stmt).scalar_one_or_none()

    def names_by_ids(self, ids) -> dict[int, str]:
        stmt = select(Usuario.id_usuario, Usuario.nombres, Usuario.apellidos).where(Usuario.id_usuario.in_(ids))
        return {r.id_usuario: f"{r.nombres} {r.apellidos}" for r in db.session.execute(stmt)}


class SesionRepository:
    def add(self, sesion: SesionUsuario) -> SesionUsuario:
        db.session.add(sesion)
        db.session.flush()  # obtiene el id generado por la base
        return sesion

    def get(self, id_sesion: int) -> SesionUsuario | None:
        return db.session.get(SesionUsuario, id_sesion)