"""Lógica de negocio de autenticación. No usa Flask ni escribe SQL: solo reglas."""
from dataclasses import dataclass

from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.core.errors.exceptions import (
    AccountInactive,
    InvalidCredentials,
    NoRoleAssigned,
    SessionClosed,
    SessionExpired,
)
from app.core.security import session_policy
from app.core.security.hashing import burn_verification_time, verify_password
from app.core.security.rbac import Principal
from app.extensions import db
from app.modules.auth.models.auth import SesionUsuario, Usuario
from app.modules.auth.repositories.auth_repository import SesionRepository, UsuarioRepository


@dataclass(frozen=True)
class LoginResult:
    usuario: Usuario
    sesion: SesionUsuario


class AuthService:
    def __init__(self, idle_minutes: int = 15, usuarios=None, sesiones=None):
        self.idle_minutes = idle_minutes
        self.usuarios = usuarios or UsuarioRepository()
        self.sesiones = sesiones or SesionRepository()

    def login(self, nombre_usuario: str, contrasena: str, ip: str | None = None) -> LoginResult:
        """RF-01.1 y RF-01.2: valida credenciales; ante datos inválidos rechaza con un mensaje."""
        usuario = self.usuarios.get_by_nombre_usuario(nombre_usuario)
        if usuario is None:
            burn_verification_time(contrasena)
            raise InvalidCredentials()
        if not verify_password(usuario.hash_contrasena, contrasena):
            raise InvalidCredentials()
        if usuario.estado != "activo":
            raise AccountInactive()
        if not usuario.roles:
            raise NoRoleAssigned()

        now = clock.now()
        with unit_of_work():
            sesion = self.sesiones.add(
                SesionUsuario(
                    id_usuario=usuario.id_usuario,
                    iniciada_en=now,
                    ultima_actividad=now,
                    expira_en=session_policy.new_expiry(now, self.idle_minutes),
                    direccion_ip=ip,
                )
            )
        return LoginResult(usuario=usuario, sesion=sesion)

    def authenticate_session(self, id_sesion: int) -> Principal:
        """RNF-02.3: valida la sesión y renueva la inactividad; si pasaron 15 minutos, la cierra."""
        sesion = self.sesiones.get(id_sesion)
        if sesion is None or sesion.cerrada_en is not None:
            raise SessionClosed()

        now = clock.now()
        if session_policy.is_expired(sesion.expira_en, now):
            sesion.cerrada_en = sesion.expira_en
            db.session.commit()
            raise SessionExpired()

        usuario = sesion.usuario
        if usuario.estado != "activo":
            raise SessionClosed()

        with unit_of_work():
            sesion.ultima_actividad = now
            sesion.expira_en = session_policy.new_expiry(now, self.idle_minutes)

        return Principal(
            id_usuario=usuario.id_usuario,
            id_sesion=sesion.id_sesion,
            nombre_usuario=usuario.nombre_usuario,
            nombres=usuario.nombres,
            apellidos=usuario.apellidos,
            roles=usuario.nombres_roles,
        )

    def logout(self, id_sesion: int) -> None:
        sesion = self.sesiones.get(id_sesion)
        if sesion is not None and sesion.cerrada_en is None:
            with unit_of_work():
                sesion.cerrada_en = clock.now()
