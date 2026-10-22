# SESCO — Software Escolar de Control y Observación

Sistema de control y seguimiento de la asistencia de estudiantes de una unidad
educativa, con registro mediante código QR dinámico, justificaciones de
ausencia, avisos a las familias, seguimiento de casos y reportes de gestión.

- **Backend:** Flask 3 + SQLAlchemy + PostgreSQL, arquitectura por capas.
- **Frontend:** React 19 + TypeScript + Vite.
- **Zona horaria:** `America/La_Paz` (UTC−4). Toda la aplicación usa
  `app/core/clock.py`; nunca `datetime.now()` ni `datetime.utcnow()`.

Documentación: [`docs/api.md`](docs/api.md) (contrato de la API),
[`docs/requisitos/especificacion.md`](docs/requisitos/especificacion.md)
(requisitos), [`docs/adr/`](docs/adr/) (decisiones de arquitectura) y
[`docs/diagramas/`](docs/diagramas/) (diagramas).

---

## 1. Requisitos

| Herramienta | Versión |
|---|---|
| Python | 3.11 o superior |
| Node.js | 20 o superior |
| PostgreSQL | 14 o superior |

## 2. Base de datos

### Opción A — PostgreSQL local (recomendado en desarrollo)

1. Crear la base y el rol de la aplicación:

   ```sql
   CREATE ROLE asistencia_user LOGIN PASSWORD 'cambia_esto';
   CREATE DATABASE sesco_db OWNER asistencia_user;
   CREATE DATABASE sesco_test OWNER asistencia_user;
   ```

2. Cargar el esquema y los datos de demostración en **ambas** bases:

   ```powershell
   psql -U postgres -d sesco_db -f infra/postgres/init.sql
   psql -U postgres -d sesco_test -f infra/postgres/init.sql
   ```

   `infra/postgres/init.sql` crea el esquema `sesco` con sus 31 tablas, la vista
   `v_asistencia_diaria` y los datos de demostración (71 usuarios, 32
   estudiantes, 30 tutores, 8 profesores, 192 sesiones de clase y 1536
   asistencias).

3. Dar permisos al rol de la aplicación:

   ```sql
   GRANT USAGE, CREATE ON SCHEMA sesco TO asistencia_user;
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sesco TO asistencia_user;
   GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA sesco TO asistencia_user;
   ```

### Opción B — Docker

```powershell
cd infra
docker compose up -d
```

## 3. Backend

```powershell
cd backend
python -m venv ..\venv
..\venv\Scripts\pip install -r requirements\dev.txt
Copy-Item .env.example .env     # y rellena DATABASE_URL, TEST_DATABASE_URL y las claves
..\venv\Scripts\python wsgi.py
```

El API queda en `http://localhost:5000` y la comprobación de estado en
`http://localhost:5000/api/health`.

> `SECRET_KEY`, `JWT_SECRET_KEY` y `TOTP_ENCRYPTION_KEY` deben ser valores
> aleatorios distintos entre sí. En producción la aplicación se niega a
> arrancar si se dejan con el valor `cambia_esto`.

## 4. Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env     # VITE_API_URL=/api
npm run dev
```

La aplicación queda en `http://localhost:5173`. Con `VITE_API_URL=/api` las
llamadas pasan por el proxy de Vite hacia `http://localhost:5000`, lo que evita
CORS y el mixed content.

El certificado autofirmado que genera `@vitejs/plugin-basic-ssl` sirve para
probar el lector de QR desde el celular (la cámara exige un contexto seguro).
En el mismo equipo puedes desactivarlo con `VITE_USE_SSL=false` en
`frontend/.env` y trabajar en `http://localhost`.

## 5. Datos de demostración

Todos los usuarios de prueba usan la contraseña `Demo1234!`.

| Usuario | Rol | Puede |
|---|---|---|
| `directora.mquispe` | director | Todo: administrar, configurar, autorizar, auditar |
| `prof.cmamani` | profesor | Registrar asistencia, observar estudiantes de sus cursos |
| `tutor1` | tutor | Ver a sus hijos, solicitar justificaciones |
| `estudiante1` | estudiante | Ver su credencial QR y su asistencia |

Los scripts de `scripts/` dejan la base lista para probar:

```powershell
cd backend

# Contraseñas reales (Argon2) para los usuarios de demostración
..\venv\Scripts\python ..\scripts\seed_passwords.py

# Credenciales QR por estudiante, con el secreto cifrado
..\venv\Scripts\python ..\scripts\seed_credenciales.py

# Horario de clases de los próximos días lectivos y asistencias pendientes
..\venv\Scripts\python ..\scripts\seed_sesiones.py --dias 20
```

Los tres aceptan `--base sesco_test` para trabajar sobre la base de pruebas.

## 6. Tests y verificaciones

```powershell
cd backend
..\venv\Scripts\python -m pytest -q                     # unit, integration y e2e
..\venv\Scripts\lint-imports                             # reglas de arquitectura
..\venv\Scripts\python -m ruff check app tests           # estilo
..\venv\Scripts\python ..\scripts\verificar_modelos.py   # modelos contra el esquema
..\venv\Scripts\python ..\scripts\smoke_test.py          # una petición a cada endpoint

cd ..\frontend
npm run lint
npm run build
```

`verificar_modelos.py` compara, tabla por tabla y columna por columna, los
modelos SQLAlchemy con el esquema real de la base de datos: es la forma
rápida de saber si el modelo se quedó atrás.

`smoke_test.py` comprueba que todas las rutas responden y que el flujo de
registro por QR funciona de principio a fin (el estudiante muestra su
credencial, el docente la escanea y el mismo código no se acepta dos veces).
No deja rastros en los datos de demostración.

Las pruebas de carga están en `backend/tests/performance/locustfile.py`:

```powershell
cd backend
..\venv\Scripts\locust -f tests/performance/locustfile.py --host http://localhost:5000
```

## 7. Estructura

```
backend/
  app/
    core/            # config, errores, seguridad, base de datos, texto, reloj, logs
    modules/         # un módulo por caso de uso
      <módulo>/
        api/         # rutas (Flask) y esquemas (Pydantic)
        services/    # reglas de negocio
        repositories/# acceso a datos
        models/      # mapeo SQLAlchemy
    jobs/            # tareas programadas
  tests/             # unit, integration, e2e, performance
frontend/
  src/
    app/             # router y proveedores
    shared/          # cliente HTTP, tipos, guardas, componentes de interfaz
    features/        # un módulo por caso de uso (api, hooks, pages, types)
    styles/          # variables de diseño
infra/
  postgres/init.sql  # esquema + datos de demostración
  docker-compose.yml
  nginx/nginx.conf
docs/                # api, requisitos, adr, diagramas
scripts/             # datos de demostración y verificación
```

### Módulos del backend

| Módulo | Qué hace |
|---|---|
| `auth` | Sesión con cierre por inactividad (15 min), Argon2, RBAC |
| `students` | CRUD, inscripción, observaciones, vínculo con tutores |
| `qr` | Credencial TOTP por estudiante, cifrada; anti-replay de 20 s |
| `attendance` | Registro por QR y manual, clasificación por parámetros |
| `settings` | Parámetros de asistencia de la unidad educativa |
| `justifications` | Solicitud, revisión y efecto sobre la asistencia |
| `announcements` | Avisos institucionales y avisos de inasistencia docente |
| `notifications` | Avisos dirigidos a cada usuario |
| `followup` | Detección de patrones y alertas de seguimiento |
| `meetings` | Citas con tutores para revisar un caso |
| `reports` | Resúmenes, reporte de asistencia y detalle por estudiante |
| `audit` | Rastro de las operaciones sensibles |
| `jobs` | Detección programada y purga de la bitácora |

## 8. Endpoints

El detalle completo, con formatos de petición y códigos de error, está en
[`docs/api.md`](docs/api.md). Resumen:

| Método | Ruta | Rol |
|---|---|---|
| GET | `/api/health` | público |
| POST | `/api/auth/login` | público |
| POST | `/api/auth/logout` | autenticado |
| GET | `/api/auth/me` | autenticado |
| GET | `/api/students` | autenticado (filtrado por rol) |
| GET | `/api/students/<id>` | autenticado |
| POST/PUT/DELETE | `/api/students[/<id>]` | director |
| GET/POST | `/api/students/<id>/observaciones` | director, profesor |
| POST | `/api/students/<id>/tutores` | director |
| GET | `/api/qr/me/code` | autenticado (estudiante) |
| GET | `/api/qr/student/<id>` | director, profesor |
| POST | `/api/qr/verify` | director, profesor |
| POST | `/api/qr/student/<id>/renovar` | director |
| POST | `/api/attendance/registrar` | director, profesor |
| GET | `/api/attendance/hoy` | director, profesor |
| GET | `/api/attendance/sesion/<id>` | director, profesor |
| POST | `/api/attendance/sesion/<id>/marcar` | director, profesor |
| GET | `/api/attendance/estudiante/<id>` | autenticado |
| GET/PUT | `/api/settings/attendance` | autenticado / director |
| GET/POST | `/api/justifications` | director, profesor, tutor / tutor |
| GET | `/api/justifications/<id>` | director, profesor, tutor |
| PUT | `/api/justifications/<id>/estado` | director |
| GET | `/api/notifications` | autenticado |
| GET | `/api/notifications/no-leidas` | autenticado |
| PUT | `/api/notifications/<id>/leer` | autenticado |
| PUT | `/api/notifications/leer-todas` | autenticado |
| POST | `/api/notifications` | director |
| GET/POST | `/api/announcements` | autenticado / director |
| GET/PUT | `/api/announcements/<id>` | autenticado / director |
| POST | `/api/announcements/<id>/publicar` | director |
| PUT | `/api/announcements/<id>/leer` | autenticado |
| GET/POST | `/api/announcements/inasistencia-docente` | director, profesor / director |
| GET | `/api/followup/alertas` | director, profesor, tutor |
| POST | `/api/followup/alertas` | director, profesor |
| PUT | `/api/followup/alertas/<id>/estado` | director, profesor |
| POST | `/api/followup/detectar` | director |
| GET | `/api/followup/estudiante/<id>` | director, profesor, tutor |
| GET/POST | `/api/meetings` | director, profesor, tutor / director, profesor |
| PUT | `/api/meetings/<id>/estado` | director, profesor |
| GET | `/api/reports/resumen` | director, profesor |
| GET | `/api/reports/asistencia` | director, profesor |
| GET | `/api/reports/estudiante/<id>` | director, profesor, tutor |
| GET | `/api/reports/diario` | director, profesor |
| GET | `/api/audit` | director |
| GET | `/api/audit/<id>` | director |

## 9. Pantallas del frontend

| Ruta | Pantalla | Rol |
|---|---|---|
| `/login` | Ingreso al sistema | público |
| `/panel` | Resumen y accesos según el rol | autenticado |
| `/escaner` | Lector de QR y registro manual | director, profesor |
| `/asistencia` | Clases del día y estado de cada estudiante | director, profesor |
| `/estudiantes` | Padrón, ficha, observaciones y tutores | director, profesor, tutor |
| `/mi-qr` | Credencial QR del estudiante | estudiante |
| `/consulta-qr` | Credencial de un estudiante y renovación | director, profesor |
| `/justificaciones` | Solicitud y revisión de justificaciones | director, profesor, tutor |
| `/seguimiento` | Alertas de inasistencia y tardanzas | director, profesor, tutor |
| `/citas` | Citas con los tutores | director, profesor, tutor |
| `/avisos` | Avisos institucionales | todos |
| `/avisos-inasistencia-docente` | Avisos de inasistencia docente | director, profesor |
| `/notificaciones` | Notificaciones de la cuenta | todos |
| `/reportes` | Resumen, reporte por estudiante y del día | director, profesor |
| `/configuracion` | Parámetros de asistencia | director |
| `/auditoria` | Bitácora de operaciones | director |

## 10. Probarlo desde el celular

El lector de QR necesita la cámara, y los navegadores solo dan acceso a ella
en un origen seguro (HTTPS). Hay dos formas de accomplishes.

### Opción A — Red local (sin internet)

El servidor de Vite ya escucha en todas las interfaces (`host: 0.0.0.0`), así
que el celular puede entrar con la IP del equipo:

```
https://192.168.100.218:5173
```

Para esto hace falta `VITE_USE_SSL=true` en `frontend/.env`: el plugin SSL de
Vite genera un certificado autofirmado que da el contexto seguro. El celular
mostrará un aviso de certificado; hay que aceptar "continuar" una vez.

La IP puede cambiar según la red; se puede ver en la salida de `npm run dev`.

### Opción B — Túnel de ngrok (desde cualquier red)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\iniciar_celular.ps1
```

El script levanta el backend, el frontend y el túnel, y muestra la dirección
pública. Se publica **el servidor de Vite** y no el backend porque el proxy
de Vite ya reenvía las llamadas de `/api`: así la aplicación completa queda
bajo un único dominio HTTPS y la cámara funciona.

La primera vez ngrok muestra su aviso: hay que tocar **"Visit Site"**. A
partir de ahí queda en una cookie y funciona sin interrupciones.

Equivalencia manual:

```powershell
cd frontend
npm run dev

# en otra terminal
ngrok http 5173
```

**Detalles importantes**

| Detalle | Por qué importa |
|---|---|
| `server.allowedHosts` en `vite.config.ts` | Vite 8 rechaza con **403** cualquier host que no conozca, incluido el dominio de ngrok. Los dominios de ngrok y los de red local están ya en la lista. |
| `VITE_API_URL=/api` | Las llamadas son relativas: pasan por el proxy de Vite y no hay CORS ni *mixed content*. |
| `VITE_USE_SSL=false` al usar ngrok | ngrok ya termina el TLS; si Vite también sirve HTTPS, el túnel no puede conectarse. |
| `CORS_ORIGINS` en `backend/.env` | Solo importa si se separa el frontend y la API en dominios distintos. Con el proxy no hace falta. |

Para añadir un dominio propio (por ejemplo un túnel fijo), basta con ponerlo
en `VITE_ALLOWED_HOSTS` en `frontend/.env`, separado por comas:

```
VITE_ALLOWED_HOSTS=sesco.mi-colegio.edu.bo
```

**Aviso de seguridad:** con el túnel abierto, cualquiera que conozca la
dirección puede entrar al sistema con una cuenta de demostración. Es una
herramienta de pruebas, no un despliegue: para producción usa `infra/nginx`
y desactiva los datos de demostración.

## 11. Despliegue

`infra/docker-compose.yml` levanta PostgreSQL con el esquema ya cargado.
`infra/nginx/nginx.conf` sirve el frontend compilado y reenvía `/api` al
backend. Para producción, define `FLASK_ENV=production` y cambia las tres
claves por valores aleatorios.
