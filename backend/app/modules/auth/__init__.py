"""Interfaz pública del módulo auth. Otros módulos solo importan desde aquí."""
from app.modules.auth.api.guards import auth_required, current_principal
from app.modules.auth.api.routes import bp
from app.modules.auth.services.directory import display_names

__all__ = ["bp", "auth_required", "current_principal", "display_names"]
