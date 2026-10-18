"""Vínculo entre estudiante y tutor. El vínculo solo vale cuando el director lo confirma. RD-02.2."""
from app.core import clock
from app.core.database.unit_of_work import unit_of_work
from app.core.errors.exceptions import DuplicateRecord, InvalidData, NotFound
from app.modules.auth import display_names
from app.modules.students.models.guardian_link import EstudianteTutor
from app.modules.students.repositories.students_repository import GuardianLinkRepository


class GuardianLinkService:
    def __init__(self, repo=None):
        self.repo = repo or GuardianLinkRepository()

    def list_for_student(self, id_estudiante: int) -> list[dict]:
        rows = self.repo.list_for_student(id_estudiante)
        nombres = display_names(t.id_usuario for _, t in rows)
        return [
            {
                "id_tutor": t.id_tutor,
                "nombre": nombres.get(t.id_usuario, ""),
                "parentesco": v.parentesco,
                "es_contacto_principal": v.es_contacto_principal,
                "confirmado": v.confirmado,
            }
            for v, t in rows
        ]

    def link(self, id_estudiante: int, id_tutor: int, parentesco: str, es_principal: bool) -> None:
        tutor = self.repo.get_tutor(id_tutor)
        if tutor is None or tutor.estado in ("rechazado", "inactivo"):
            raise NotFound("El tutor indicado no existe o no está habilitado.", "Verifique el tutor e intente nuevamente.")
        if self.repo.get_link(id_estudiante, id_tutor) is not None:
            raise DuplicateRecord("Ese tutor ya está vinculado al estudiante.", "Revise la lista de tutores del estudiante.")
        if es_principal and self.repo.principal_link(id_estudiante) is not None:
            raise InvalidData(
                "El estudiante ya tiene un contacto principal.", "Cambie el contacto principal actual antes de asignar otro."
            )
        with unit_of_work():
            self.repo.add_link(
                EstudianteTutor(
                    id_estudiante=id_estudiante,
                    id_tutor=id_tutor,
                    parentesco=parentesco,
                    es_contacto_principal=es_principal,
                    confirmado=False,
                )
            )

    def confirm(self, id_estudiante: int, id_tutor: int, director_id: int) -> None:
        vinculo = self.repo.get_link(id_estudiante, id_tutor)
        if vinculo is None:
            raise NotFound("Ese tutor no está vinculado al estudiante.", "Primero vincule al tutor y luego confirme.")
        if vinculo.confirmado:
            return
        with unit_of_work():
            vinculo.confirmado = True
            vinculo.confirmado_por = director_id
            vinculo.confirmado_en = clock.now()