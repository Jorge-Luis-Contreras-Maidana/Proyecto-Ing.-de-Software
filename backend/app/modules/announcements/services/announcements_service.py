"""Reglas de negocio de los avisos institucionales. No usa Flask ni escribe SQL."""
from dataclasses import dataclass

from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.core.errors.exceptions import InvalidData, NotFound, PermissionDenied
from app.core.security.rbac import Principal
from app.modules.announcements.models.announcements import Aviso, AvisoDestinatarioRol, LecturaAviso
from app.modules.announcements.repositories.announcements_repository import AnnouncementsRepository
from app.modules.attendance.models.attendance import AvisoInasistenciaDocente
from app.modules.audit.services.audit_logger import AuditLogger

# Estados que admite la tabla de avisos.
ESTADOS = ("borrador", "publicado", "archivado")


@dataclass(frozen=True)
class AvisoView:
    """Aviso con los datos derivados que necesita la respuesta de la API."""

    aviso: Aviso
    roles_destinatarios: tuple[str, ...]
    total_lectores: int
    leido: bool


class AnnouncementsService:
    def __init__(self, repo=None, auditor=None):
        self.repo = repo or AnnouncementsRepository()
        self.auditor = auditor or AuditLogger()

    # ---------- helpers ----------
    @staticmethod
    def _es_director(principal: Principal) -> bool:
        return "director" in principal.roles

    def _resolver_roles(self, nombres) -> list:
        """Convierte nombres de rol en filas de la tabla de roles."""
        if not nombres:
            return []
        unicos = []
        for nombre in nombres:
            limpio = (nombre or "").strip().lower()
            if limpio and limpio not in unicos:
                unicos.append(limpio)
        if not unicos:
            return []
        roles = self.repo.roles_por_nombre(unicos)
        encontrados = {r.nombre for r in roles}
        faltantes = [n for n in unicos if n not in encontrados]
        if faltantes:
            raise InvalidData(
                f"El rol '{faltantes[0]}' no existe.",
                "Use uno de los roles: director, profesor, tutor o estudiante.",
            )
        return roles

    def _fila(self, row) -> AvisoView:
        aviso, roles, total_lectores, leido = row
        return AvisoView(
            aviso=aviso,
            roles_destinatarios=tuple(roles or ()),
            total_lectores=int(total_lectores or 0),
            leido=bool(leido),
        )

    # ---------- lectura ----------
    def listar(self, principal: Principal, estado=None, solo_no_leidos=False, page=1, per_page=20):
        """Listado de avisos visibles para el usuario.

        La dirección ve todos los avisos (también los borradores); el resto de los
        usuarios solo ve los avisos publicados cuyo destino coincide con sus roles
        o que no tienen roles destinatarios.
        """
        es_director = self._es_director(principal)
        if estado is not None:
            if estado not in ESTADOS:
                raise InvalidData(
                    "El estado indicado no es válido.",
                    "Use uno de los estados: borrador, publicado o archivado.",
                )
            if not es_director and estado != "publicado":
                raise PermissionDenied(
                    "Solo la dirección puede consultar avisos en borrador o archivados.",
                    "Consulte los avisos publicados.",
                )
        rows, total = self.repo.listar(
            principal.roles, es_director, principal.id_usuario, estado, solo_no_leidos, page, per_page
        )
        return [self._fila(r) for r in rows], total

    def obtener(self, principal: Principal, id_aviso: int) -> AvisoView:
        row = self.repo.obtener(id_aviso, principal.roles, self._es_director(principal), principal.id_usuario)
        if row is None:
            raise NotFound("No se encontró el aviso.", "Verifique el aviso o regrese a la lista.")
        return self._fila(row)

    # ---------- escritura (director) ----------
    def crear(self, principal: Principal, data) -> AvisoView:
        estado = data.estado or "borrador"
        if estado not in ESTADOS:
            raise InvalidData(
                "El estado indicado no es válido.",
                "Use 'borrador' o 'publicado'.",
            )
        roles = self._resolver_roles(data.roles_destinatarios)
        ahora = clock.now()
        with unit_of_work():
            # La tabla exige publicado_en NOT NULL: en un borrador se guarda la fecha
            # de creación y se reemplaza al publicar.
            aviso = self.repo.add_aviso(
                Aviso(
                    titulo=data.titulo.strip(),
                    contenido=data.contenido.strip(),
                    creado_por=principal.id_usuario,
                    publicado_en=ahora,
                    importante=bool(data.importante),
                    estado=estado,
                )
            )
            for rol in roles:
                self.repo.add_destinatario(
                    AvisoDestinatarioRol(id_aviso=aviso.id_aviso, id_rol=rol.id_rol)
                )
        self.auditor.registrar(
            principal.id_usuario,
            "CREAR_AVISO",
            "avisos",
            str(aviso.id_aviso),
            f"Aviso '{aviso.titulo}' creado en estado '{estado}'.",
        )
        return self.obtener(principal, aviso.id_aviso)

    def actualizar(self, principal: Principal, id_aviso: int, data) -> AvisoView:
        fila = self.repo.get(id_aviso)
        if fila is None:
            raise NotFound("No se encontró el aviso.", "Verifique el aviso o regrese a la lista.")
        cambios = data.model_dump(exclude_unset=True)
        roles = None
        if "roles_destinatarios" in cambios:
            roles = self._resolver_roles(cambios.pop("roles_destinatarios"))
        with unit_of_work():
            if "titulo" in cambios and cambios["titulo"] is not None:
                fila.titulo = cambios["titulo"].strip()
            if "contenido" in cambios and cambios["contenido"] is not None:
                fila.contenido = cambios["contenido"].strip()
            if "importante" in cambios and cambios["importante"] is not None:
                fila.importante = bool(cambios["importante"])
            if "estado" in cambios and cambios["estado"] is not None:
                if cambios["estado"] not in ESTADOS:
                    raise InvalidData(
                        "El estado indicado no es válido.",
                        "Use 'borrador', 'publicado' o 'archivado'.",
                    )
                fila.estado = cambios["estado"]
                if cambios["estado"] == "publicado":
                    fila.publicado_en = clock.now()
            if roles is not None:
                self.repo.borrar_destinatarios(fila.id_aviso)
                for rol in roles:
                    self.repo.add_destinatario(
                        AvisoDestinatarioRol(id_aviso=fila.id_aviso, id_rol=rol.id_rol)
                    )
        return self.obtener(principal, id_aviso)

    def publicar(self, principal: Principal, id_aviso: int) -> AvisoView:
        fila = self.repo.get(id_aviso)
        if fila is None:
            raise NotFound("No se encontró el aviso.", "Verifique el aviso o regrese a la lista.")
        if fila.estado == "publicado":
            raise InvalidData("El aviso ya está publicado.", "Consulte el listado de avisos publicados.")
        with unit_of_work():
            fila.estado = "publicado"
            fila.publicado_en = clock.now()
        self.auditor.registrar(
            principal.id_usuario,
            "PUBLICAR_AVISO",
            "avisos",
            str(fila.id_aviso),
            f"Aviso '{fila.titulo}' publicado.",
        )
        return self.obtener(principal, id_aviso)

    # ---------- lectura del aviso ----------
    def marcar_leido(self, principal: Principal, id_aviso: int) -> AvisoView:
        # Comprueba que el aviso sea visible para el usuario antes de registrar la lectura.
        self.obtener(principal, id_aviso)
        ahora = clock.now()
        with unit_of_work():
            lectura = self.repo.get_lectura(id_aviso, principal.id_usuario)
            if lectura is None:
                lectura = self.repo.add_lectura(
                    LecturaAviso(
                        id_aviso=id_aviso,
                        id_usuario=principal.id_usuario,
                        entregado_en=ahora,
                        leido_en=ahora,
                    )
                )
            elif lectura.leido_en is None:
                if lectura.entregado_en is None:
                    lectura.entregado_en = ahora
                lectura.leido_en = ahora
        return self.obtener(principal, id_aviso)

    # ---------- avisos de inasistencia docente ----------
    def listar_inasistencia(self, principal: Principal):
        id_profesor = None
        if not self._es_director(principal):
            id_profesor = self.repo.id_profesor_de_usuario(principal.id_usuario)
            if id_profesor is None:
                return []
        return self.repo.listar_inasistencia(id_profesor)

    def crear_inasistencia(self, principal: Principal, data):
        profesor = self.repo.get_profesor(data.id_profesor)
        if profesor is None:
            raise NotFound("El docente indicado no existe.", "Elija un docente de la lista.")
        if data.id_sesion_clase is not None and self.repo.get_sesion(data.id_sesion_clase) is None:
            raise NotFound("La sesión de clase indicada no existe.", "Elija una sesión de clase válida.")
        with unit_of_work():
            aviso = self.repo.add_inasistencia(
                self._nueva_inasistencia(data, profesor.id_profesor)
            )
        self.auditor.registrar(
            principal.id_usuario,
            "CREAR_AVISO_INASISTENCIA_DOCENTE",
            "avisos_inasistencia_docente",
            str(aviso.id_aviso_docente),
            f"Aviso de inasistencia docente del docente {profesor.id_profesor}.",
        )
        return aviso

    def _nueva_inasistencia(self, data, id_profesor: int):
        return AvisoInasistenciaDocente(
            id_profesor=id_profesor,
            id_sesion_clase=data.id_sesion_clase,
            fecha_afectada=data.fecha_afectada,
            motivo=data.motivo.strip(),
            enviado_en=clock.now(),
            estado="pendiente",
            revisado_por=None,
            revisado_en=None,
            decision=None,
        )
