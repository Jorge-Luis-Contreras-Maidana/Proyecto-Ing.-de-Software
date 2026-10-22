# Arquitectura del backend

```mermaid
flowchart TB
    subgraph entrada["Entrada"]
        HTTP["Peticiones HTTP"]
    end

    subgraph app["app"]
        subgraph core["core — transversal, no conoce los módulos"]
            CFG["config<br/>ajustes, entornos"]
            ERR["errors<br/>excepciones y mensajes"]
            SEC["security<br/>hash, rbac, sesión, cifrado"]
            DBL["database<br/>base, sesión, unit_of_work"]
            TXT["text<br/>búsqueda sin tildes"]
            CLK["clock<br/>hora de Bolivia"]
        end

        subgraph modules["modules — un caso de uso por carpeta"]
            direction LR
            AUTH["auth"]
            STU["students"]
            QR["qr"]
            ATT["attendance"]
            JUS["justifications"]
            ANN["announcements"]
            NOT["notifications"]
            FOL["followup"]
            MEE["meetings"]
            REP["reports"]
            AUD["audit"]
            SET["settings"]
        end
    end

    BD[("PostgreSQL<br/>esquema sesco")]

    HTTP --> modules
    modules --> core
    modules --> BD
    DBL --> BD

    classDef coreBox fill:#e8f0fe,stroke:#4285f4
    classDef modBox fill:#fef7e0,stroke:#f9ab00
    class CFG,ERR,SEC,DBL,TXT,CLK coreBox
    class AUTH,STU,QR,ATT,JUS,ANN,NOT,FOL,MEE,REP,AUD,SET modBox
```

## Las cuatro capas de un módulo

```mermaid
flowchart LR
    API["api<br/>rutas y esquemas"] --> SVC["services<br/>reglas de negocio"] --> REPO["repositories<br/>acceso a datos"] --> MOD["models<br/>mapeo de tablas"]
    API -.-> ERR["core/errors"]
    SVC -.-> SEC["core/security"]
    SVC -.-> CLK["core/clock"]
    REPO -.-> DBL["core/database"]
```

- **api**: recibe la petición, valida el cuerpo con Pydantic y devuelve JSON.
  Es la única capa que conoce Flask.
- **services**: decide. No usa Flask ni escribe SQL.
- **repositories**: habla con la base de datos.
- **models**: mapea las tablas.

## Reglas que se verifican automáticamente

```powershell
cd backend
..\venv\Scripts\lint-imports                    # el núcleo no depende de los módulos
..\venv\Scripts\python.exe ..\scripts\verificar_modelos.py   # los modelos coinciden con el esquema
..\venv\Scripts\python.exe -m pytest -q          # las reglas, sin servidor
```

Los contratos de `import-linter` están en `backend/.importlinter` y la
verificación de modelos en `scripts/verificar_modelos.py`. Esta última
compara, tabla por tabla y columna por columna, los modelos SQLAlchemy con el
esquema real de la base de datos.

## Decisión de diseño

La arquitectura y sus alternativas están en
[`docs/adr/0001-arquitectura-por-capas.md`](../adr/0001-arquitectura-por-capas.md).
