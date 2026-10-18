"""Crea la estructura del proyecto. Uso: python crear_estructura.py"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent

MODULES = ["auth", "students", "qr", "attendance", "notifications",
           "followup", "meetings", "announcements", "reports", "audit", "settings"]

# Archivos extra por módulo (ruta relativa a la carpeta del módulo)
EXTRA = {
    "students": ["services/guardian_link_service.py", "models/guardian_link.py"],
    "qr": ["services/totp_service.py"],
    "attendance": ["services/attendance_rules.py"],
    "notifications": ["channels/base.py", "channels/email_channel.py",
                      "channels/push_channel.py"],
    "followup": ["services/pattern_detector.py"],
    "reports": ["services/report_builder.py"],
    "audit": ["services/audit_logger.py"],
}

GITIGNORE = """.venv/
__pycache__/
*.pyc
.env
node_modules/
dist/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
*.log
"""

ENV_EXAMPLE = """FLASK_ENV=development
DATABASE_URL=postgresql+psycopg://asistencia_user:cambia_esto@localhost:5432/asistencia_db
SECRET_KEY=cambia_esto
JWT_SECRET_KEY=cambia_esto
TOTP_ENCRYPTION_KEY=cambia_esto
TZ=America/La_Paz
"""

REQ_BASE = """Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-JWT-Extended
Flask-Cors
psycopg[binary]
pydantic
argon2-cffi
pyotp
APScheduler
python-dotenv
gunicorn
"""

REQ_DEV = """-r base.txt
pytest
pytest-cov
factory-boy
ruff
mypy
import-linter
locust
"""

REQ_PROD = "-r base.txt\n"

IMPORTLINTER = """[importlinter]
root_package = app

[importlinter:contract:core-independiente]
name = core no depende de modules
type = forbidden
source_modules = app.core
forbidden_modules = app.modules
"""

EXTENSIONS = """{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "mtxr.sqltools",
    "mtxr.sqltools-driver-pg"
  ]
}
"""

files = {}  # ruta relativa -> contenido inicial


def add(path, content=""):
    files[path] = content


# ---------- Raíz ----------
for p in ["README.md", ".editorconfig", "scripts/seed_data.py",
          "docs/requisitos/especificacion.md", "docs/diagramas/.gitkeep",
          "docs/adr/0001-arquitectura-por-capas.md",
          "infra/docker-compose.yml", "infra/nginx/nginx.conf",
          "infra/postgres/init.sql", ".vscode/settings.json",
          ".vscode/launch.json"]:
    add(p)
add(".gitignore", GITIGNORE)
add(".vscode/extensions.json", EXTENSIONS)

# ---------- Backend ----------
add("backend/wsgi.py")
add("backend/pytest.ini")
add("backend/.env.example", ENV_EXAMPLE)
add("backend/.importlinter", IMPORTLINTER)
add("backend/requirements/base.txt", REQ_BASE)
add("backend/requirements/dev.txt", REQ_DEV)
add("backend/requirements/prod.txt", REQ_PROD)

for p in ["app/__init__.py", "app/extensions.py",
          "app/config/base.py", "app/config/development.py",
          "app/config/production.py", "app/config/testing.py",
          "app/core/clock.py",
          "app/core/security/hashing.py", "app/core/security/tokens.py",
          "app/core/security/rbac.py", "app/core/security/session_policy.py",
          "app/core/errors/exceptions.py", "app/core/errors/handlers.py",
          "app/core/errors/messages.py",
          "app/core/database/base.py", "app/core/database/session.py",
          "app/core/database/unit_of_work.py",
          "app/core/logs/setup.py",
          "app/jobs/scheduler.py", "app/jobs/detect_attendance_job.py",
          "app/jobs/purge_audit_job.py",
          "tests/conftest.py", "tests/e2e/test_flujo_asistencia_qr.py",
          "tests/performance/locustfile.py"]:
    add(f"backend/{p}")

for m in MODULES:
    base = f"backend/app/modules/{m}"
    add(f"{base}/__init__.py")
    add(f"{base}/api/routes.py")
    add(f"{base}/api/schemas.py")
    add(f"{base}/services/{m}_service.py")
    add(f"{base}/repositories/{m}_repository.py")
    add(f"{base}/models/{m}.py")
    for extra in EXTRA.get(m, []):
        add(f"{base}/{extra}")
    add(f"backend/tests/unit/{m}/test_{m}_service.py")
    add(f"backend/tests/integration/{m}/test_{m}_routes.py")

# __init__.py en todos los paquetes Python
for path in list(files):
    if path.endswith(".py") and path.startswith(("backend/app/", "backend/tests/")):
        parent = Path(path).parent
        while parent.as_posix() != "backend":
            files.setdefault((parent / "__init__.py").as_posix(), "")
            parent = parent.parent

# ---------- Frontend (src ya lo creó Vite) ----------
S = "frontend/src"
add("frontend/.env.example", "VITE_API_URL=http://localhost:5000/api\n")
for p in ["app/router.tsx", "app/providers/AuthProvider.tsx",
          "shared/api/httpClient.ts", "shared/api/errorMapper.ts",
          "shared/ui/.gitkeep", "shared/hooks/useAutoLogout.ts",
          "shared/guards/RequireRole.tsx", "shared/lib/formatDate.ts",
          "shared/config/env.ts", "shared/types/common.ts",
          "styles/tokens.css"]:
    add(f"{S}/{p}")

for m in MODULES:
    t = m.capitalize()
    f = f"{S}/features/{m}"
    add(f"{f}/api/{m}Api.ts")
    add(f"{f}/hooks/use{t}.ts")
    add(f"{f}/pages/{t}Page.tsx")
    add(f"{f}/types/{m}.types.ts")
    add(f"{f}/components/.gitkeep")

# ---------- Crear ----------
creados = 0
for rel, content in sorted(files.items()):
    target = ROOT / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text(content, encoding="utf-8")
        creados += 1

print(f"Listo: {creados} archivos creados en {ROOT}")