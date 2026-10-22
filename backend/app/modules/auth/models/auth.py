from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

usuarios_roles = db.Table(
    "usuarios_roles",
    db.Column("id_usuario", Integer, ForeignKey("usuarios.id_usuario"), primary_key=True),
    db.Column("id_rol", SmallInteger, ForeignKey("roles.id_rol"), primary_key=True),
)


class Rol(db.Model):
    __tablename__ = "roles"

    id_rol: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(30), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(200))


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombres: Mapped[str] = mapped_column(String(80))
    apellidos: Mapped[str] = mapped_column(String(100))
    nombre_usuario: Mapped[str] = mapped_column(String(60), unique=True)
    correo: Mapped[str | None] = mapped_column(String(150))
    telefono: Mapped[str | None] = mapped_column(String(30))
    hash_contrasena: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(15))
    debe_cambiar_contrasena: Mapped[bool] = mapped_column(Boolean)
    creado_en: Mapped[datetime] = mapped_column(DateTime)

    roles: Mapped[list[Rol]] = relationship(secondary=usuarios_roles, lazy="selectin")

    @property
    def nombres_roles(self) -> tuple[str, ...]:
        return tuple(sorted(r.nombre for r in self.roles))


class SesionUsuario(db.Model):
    __tablename__ = "sesiones_usuario"

    id_sesion: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"))
    iniciada_en: Mapped[datetime] = mapped_column(DateTime)
    ultima_actividad: Mapped[datetime] = mapped_column(DateTime)
    expira_en: Mapped[datetime] = mapped_column(DateTime)
    cerrada_en: Mapped[datetime | None] = mapped_column(DateTime)
    direccion_ip: Mapped[str | None] = mapped_column(INET)

    usuario: Mapped[Usuario] = relationship(lazy="joined")
