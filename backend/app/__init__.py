from flask import Flask, request
from flask_cors import CORS

from app.config import get_config
from app.core.errors.handlers import register_error_handlers
from app.core.logs.setup import configure_logging
from app.extensions import db, jwt
from app.modules.announcements.api.routes import bp as announcements_bp
from app.modules.attendance.api.routes import bp as attendance_bp
from app.modules.audit.api.routes import bp as audit_bp
from app.modules.auth import bp as auth_bp
from app.modules.followup.api.routes import bp as followup_bp
from app.modules.justifications.api.routes import bp as justifications_bp
from app.modules.meetings.api.routes import bp as meetings_bp
from app.modules.notifications.api.routes import bp as notifications_bp
from app.modules.qr.api.routes import bp as qr_bp
from app.modules.reports.api.routes import bp as reports_bp
from app.modules.settings.api.routes import bp as settings_bp
from app.modules.students import bp as students_bp


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)
    app.json.ensure_ascii = False

    if config.ENV_NAME == "production" and "cambia_esto" in (app.config["SECRET_KEY"], app.config["JWT_SECRET_KEY"]):
        raise RuntimeError("En producción debe definir SECRET_KEY y JWT_SECRET_KEY en el archivo .env.")
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("Falta DATABASE_URL en el archivo backend/.env.")

    db.init_app(app)
    jwt.init_app(app)
    configure_logging(app)

    # CORS permissive
    CORS(app, resources={r"/*": {"origins": "*"}})

    register_error_handlers(app, jwt)

    # Registro de módulos
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(students_bp, url_prefix="/api/students")
    app.register_blueprint(settings_bp, url_prefix="/api/settings")
    app.register_blueprint(qr_bp, url_prefix="/api/qr")
    app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
    app.register_blueprint(justifications_bp, url_prefix="/api/justifications")
    app.register_blueprint(announcements_bp, url_prefix="/api/announcements")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    app.register_blueprint(audit_bp, url_prefix="/api/audit")
    app.register_blueprint(followup_bp, url_prefix="/api/followup")
    app.register_blueprint(meetings_bp, url_prefix="/api/meetings")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")

    # Interceptor global para inyectar CORS en TODAS las respuestas (incluyendo preflights de Ngrok)
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, ngrok-skip-browser-warning'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'

        # Responder 200 OK inmediatamente a las peticiones preflight OPTIONS
        if request.method == 'OPTIONS':
            response.status_code = 200

        return response

    @app.get("/api/health")
    def health():
        return {"estado": "ok"}

    # Tareas periódicas: detección de alertas y purga de la bitácora.
    # Solo se encienden si la configuración lo permite.
    _iniciar_planificador(app)

    return app


def _iniciar_planificador(app: Flask) -> None:
    """Arranca el planificador si está disponible y la configuración lo permite.

    Si APScheduler no está instalado, la aplicación sigue funcionando: solo
    se loses tareas programadas.
    """
    try:
        from app.jobs.scheduler import init_scheduler
    except ImportError:
        app.logger.warning("APScheduler no está instalado: no habrá tareas programadas.")
        return
    init_scheduler(app)
