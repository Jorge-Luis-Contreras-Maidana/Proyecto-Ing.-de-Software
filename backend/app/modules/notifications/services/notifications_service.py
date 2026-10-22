"""Reglas de negocio de las notificaciones. No usa Flask ni escribe SQL."""
from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.core.errors.exceptions import NotFound
from app.core.security.rbac import Principal
from app.modules.audit.services.audit_logger import AuditLogger
from app.modules.auth.services.directory import display_names
from app.modules.notifications.models.notifications import Notificacion
from app.modules.notifications.repositories.notifications_repository import NotificationsRepository


class NotificationsService:
    def __init__(self, repo=None, auditor=None):
        self.repo = repo or NotificationsRepository()
        self.auditor = auditor or AuditLogger()

    # ---------- lectura ----------
    def listar(self, principal: Principal, page: int = 1, per_page: int = 20):
        """Solo el usuario ve sus propias notificaciones."""
        items, total = self.repo.listar(principal.id_usuario, page, per_page)
        return items, total, self.repo.contar_no_leidas(principal.id_usuario)

    def no_leidas(self, principal: Principal) -> int:
        return self.repo.contar_no_leidas(principal.id_usuario)

    # ---------- escritura ----------
    def marcar_leida(self, principal: Principal, id_notificacion: int) -> Notificacion:
        notificacion = self.repo.get(id_notificacion)
        # Si la notificación es de otro usuario no se revela ni su existencia.
        if notificacion is None or notificacion.id_usuario_destinatario != principal.id_usuario:
            raise NotFound("No se encontró la notificación.", "Verifique la notificación o regrese al inicio.")
        with unit_of_work():
            if notificacion.leida_en is None:
                notificacion.leida_en = clock.now()
            if notificacion.estado != "leida":
                notificacion.estado = "leida"
        return notificacion

    def leer_todas(self, principal: Principal) -> int:
        with unit_of_work():
            return self.repo.marcar_todas_leidas(principal.id_usuario, clock.now())

    def crear(
        self,
        principal: Principal,
        id_usuario_destinatario: int,
        tipo: str,
        titulo: str,
        mensaje: str,
        entidad_referencia: str | None = None,
        id_referencia: int | None = None,
    ) -> Notificacion:
        """La dirección notifica a un usuario concreto."""
        if not display_names([id_usuario_destinatario]):
            raise NotFound("El usuario destinatario no existe.", "Elija un usuario válido de la lista.")
        ahora = clock.now()
        with unit_of_work():
            notificacion = self.repo.add(
                Notificacion(
                    id_usuario_destinatario=id_usuario_destinatario,
                    tipo=tipo,
                    titulo=titulo.strip(),
                    mensaje=mensaje.strip(),
                    creada_en=ahora,
                    entregada_en=ahora,
                    leida_en=None,
                    estado="entregada",
                    entidad_referencia=entidad_referencia,
                    id_referencia=id_referencia,
                )
            )
        self.auditor.registrar(
            principal.id_usuario,
            "CREAR_NOTIFICACION",
            "notificaciones",
            str(notificacion.id_notificacion),
            f"Notificación '{notificacion.titulo}' enviada al usuario {id_usuario_destinatario}.",
        )
        return notificacion
