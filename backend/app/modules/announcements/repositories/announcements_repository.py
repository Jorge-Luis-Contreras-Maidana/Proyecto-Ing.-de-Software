"""Acceso a datos de los avisos institucionales. No aplica reglas de negocio."""
from sqlalchemy import distinct, func, or_, select

from app.extensions import db
from app.modules.announcements.models.announcements import (
    Aviso,
    AvisoDestinatarioRol,
    LecturaAviso,
)
from app.modules.attendance.models.attendance import AvisoInasistenciaDocente, SesionClase
from app.modules.auth.models.auth import Rol
from app.modules.students.models.students import Profesor


class AnnouncementsRepository:
    # ---------- consultas de avisos ----------
    def _sub_roles(self):
        """Subconsulta con los nombres de rol destinatarios de cada aviso."""
        return (
            select(
                AvisoDestinatarioRol.id_aviso,
                func.array_agg(distinct(Rol.nombre)).label("roles"),
            )
            .join(Rol, Rol.id_rol == AvisoDestinatarioRol.id_rol)
            .group_by(AvisoDestinatarioRol.id_aviso)
            .subquery()
        )

    def _select_base(self, id_usuario: int):
        """Consulta base: aviso + roles destinatarios + lectores + si el usuario ya lo leyó."""
        roles = self._sub_roles()
        total_lectores = (
            select(func.count(LecturaAviso.id_usuario))
            .where(LecturaAviso.id_aviso == Aviso.id_aviso)
            .scalar_subquery()
        )
        leido = (
            select(func.count(LecturaAviso.id_usuario))
            .where(
                LecturaAviso.id_aviso == Aviso.id_aviso,
                LecturaAviso.id_usuario == id_usuario,
                LecturaAviso.leido_en.isnot(None),
            )
            .scalar_subquery()
        )
        return (
            select(
                Aviso,
                roles.c.roles,
                total_lectores.label("total_lectores"),
                leido.label("leido"),
            )
            .select_from(Aviso)
            .outerjoin(roles, roles.c.id_aviso == Aviso.id_aviso)
        )

    def _cond_visibilidad(self, roles_usuario):
        """El aviso es visible si no tiene roles destinatarios o si coincide con los del usuario."""
        sin_destinatarios = (
            ~select(AvisoDestinatarioRol.id_aviso)
            .where(AvisoDestinatarioRol.id_aviso == Aviso.id_aviso)
            .exists()
        )
        coincide = (
            select(AvisoDestinatarioRol.id_aviso)
            .join(Rol, Rol.id_rol == AvisoDestinatarioRol.id_rol)
            .where(
                AvisoDestinatarioRol.id_aviso == Aviso.id_aviso,
                Rol.nombre.in_(list(roles_usuario)),
            )
            .exists()
        )
        return or_(sin_destinatarios, coincide)

    def _cond_no_leido(self, id_usuario: int):
        """El aviso todavía no fue leído por el usuario."""
        return (
            ~select(LecturaAviso.id_aviso)
            .where(
                LecturaAviso.id_aviso == Aviso.id_aviso,
                LecturaAviso.id_usuario == id_usuario,
                LecturaAviso.leido_en.isnot(None),
            )
            .exists()
        )

    def listar(self, roles_usuario, es_director, id_usuario, estado, solo_no_leidos, page, per_page):
        conds = []
        if estado:
            conds.append(Aviso.estado == estado)
        if not es_director:
            conds.append(self._cond_visibilidad(roles_usuario))
        if solo_no_leidos:
            conds.append(self._cond_no_leido(id_usuario))
        total = db.session.scalar(select(func.count()).select_from(Aviso).where(*conds))
        stmt = (
            self._select_base(id_usuario)
            .where(*conds)
            .order_by(Aviso.publicado_en.desc(), Aviso.id_aviso.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        return db.session.execute(stmt).all(), total

    def obtener(self, id_aviso: int, roles_usuario, es_director, id_usuario: int):
        conds = [Aviso.id_aviso == id_aviso]
        if not es_director:
            conds.append(Aviso.estado == "publicado")
            conds.append(self._cond_visibilidad(roles_usuario))
        stmt = self._select_base(id_usuario).where(*conds)
        return db.session.execute(stmt).first()

    def get(self, id_aviso: int) -> Aviso | None:
        return db.session.get(Aviso, id_aviso)

    # ---------- escritura ----------
    def add_aviso(self, aviso: Aviso) -> Aviso:
        db.session.add(aviso)
        db.session.flush()
        return aviso

    def add_destinatario(self, destino: AvisoDestinatarioRol) -> AvisoDestinatarioRol:
        db.session.add(destino)
        db.session.flush()
        return destino

    def borrar_destinatarios(self, id_aviso: int) -> None:
        for destino in db.session.execute(
            select(AvisoDestinatarioRol).where(AvisoDestinatarioRol.id_aviso == id_aviso)
        ).scalars():
            db.session.delete(destino)
        db.session.flush()

    def get_lectura(self, id_aviso: int, id_usuario: int) -> LecturaAviso | None:
        stmt = select(LecturaAviso).where(
            LecturaAviso.id_aviso == id_aviso, LecturaAviso.id_usuario == id_usuario
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def add_lectura(self, lectura: LecturaAviso) -> LecturaAviso:
        db.session.add(lectura)
        db.session.flush()
        return lectura

    # ---------- roles ----------
    def roles_por_nombre(self, nombres) -> list[Rol]:
        stmt = select(Rol).where(Rol.nombre.in_(list(nombres))).order_by(Rol.nombre)
        return db.session.execute(stmt).scalars().all()

    # ---------- avisos de inasistencia docente ----------
    def listar_inasistencia(self, id_profesor: int | None = None):
        stmt = select(AvisoInasistenciaDocente)
        if id_profesor is not None:
            stmt = stmt.where(AvisoInasistenciaDocente.id_profesor == id_profesor)
        stmt = stmt.order_by(AvisoInasistenciaDocente.fecha_afectada.desc(), AvisoInasistenciaDocente.id_aviso_docente.desc())
        return db.session.execute(stmt).scalars().all()

    def add_inasistencia(self, aviso: AvisoInasistenciaDocente) -> AvisoInasistenciaDocente:
        db.session.add(aviso)
        db.session.flush()
        return aviso

    def get_profesor(self, id_profesor: int) -> Profesor | None:
        return db.session.get(Profesor, id_profesor)

    def id_profesor_de_usuario(self, id_usuario: int) -> int | None:
        stmt = select(Profesor.id_profesor).where(Profesor.id_usuario == id_usuario)
        return db.session.execute(stmt).scalars().first()

    def get_sesion(self, id_sesion_clase: int) -> SesionClase | None:
        return db.session.get(SesionClase, id_sesion_clase)
