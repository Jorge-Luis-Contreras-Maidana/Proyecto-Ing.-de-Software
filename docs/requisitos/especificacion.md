# Especificación de requisitos de SESCO

Software Escolar de Control y Observación. Sistema de control y seguimiento de
la asistencia de estudiantes de una unidad educativa.

Los identificadores `RF-`, `RNF-` y `RD-` de este documento son los mismos que
aparecen en el código, de modo que cada regla se pueda rastrear hasta su
implementación.

---

## 1. Alcance

El sistema cubre la asistencia de los estudiantes de una unidad educativa
(La Paz, Bolivia) mediante credencial QR dinámica, la justificación de
ausencias, la comunicación con las familias, el seguimiento de los casos
problemáticos y los reportes de gestión.

Fuera de alcance: la matrícula, la evaluación académica, la planilla docente y
la administración financiera.

## 2. Actores y roles

| Rol | Descripción |
|---|---|
| `director` | Administra la unidad educativa: configura parámetros, autoriza salidas, revisa justificaciones, consulta la auditoría. |
| `profesor` | Registra la asistencia de sus cursos, observa estudiantes, genera alertas de seguimiento. |
| `tutor` | Padre, madre o tutor legal. Consulta la información de sus estudiantes, solicita justificaciones, recibe avisos. |
| `estudiante` | Consulta su credencial QR y su propio historial de asistencia. |

Un usuario puede tener más de un rol. El control de acceso se resuelve en
`app/core/security/rbac.py` y se aplica con el decorador `@auth_required(...)`.

## 3. Requisitos funcionales

### Módulo de autenticación

| ID | Requisito | Implementación |
|---|---|---|
| RF-01.1 | El sistema valida las credenciales del usuario y, si son inválidas, rechaza el acceso con un mensaje claro que no revela si el usuario existe. | `auth/services/auth_service.py` · `core/security/hashing.py` |
| RF-01.2 | Al acceder se crea una sesión con su hora de inicio, última actividad y expiración. | `auth/models/auth.py` · `SesionUsuario` |
| RF-01.3 | El acceso a cada operación depende del rol del usuario. | `core/security/rbac.py` · `auth/api/guards.py` |
| RF-01.4 | El usuario puede cerrar su sesión. | `POST /api/auth/logout` |

### Módulo de estudiantes

| ID | Requisito | Implementación |
|---|---|---|
| RF-02.1 | La dirección registra, modifica y da de baja estudiantes con su curso e inscripción en la gestión activa. | `students/services/students_service.py` |
| RF-02.2 | Los docentes registran observaciones de los estudiantes y la dirección las mantiene. | `students/services/students_service.py` |
| RF-02.3 | La dirección vincula a los tutores con los estudiantes; el vínculo solo es válido tras su confirmación. | `students/services/guardian_link_service.py` |
| RF-02.4 | La búsqueda de estudiantes ignora tildes y mayúsculas. | `core/text/search.py` |

### Módulo de credencial QR

| ID | Requisito | Implementación |
|---|---|---|
| RF-03.1 | Cada estudiante tiene su propia credencial, con un secreto TOTP cifrado en la base de datos. | `qr/services/qr_service.py` · `core/security/totp_crypto.py` |
| RF-03.2 | El código se renueva cada 20 segundos y la aplicación muestra cuánto le queda. | `qr/services/totp_service.py` |
| RF-03.3 | Un código solo sirve para el estudiante que lo emitió. | `qr/services/qr_service.py` |
| RF-03.4 | El mismo código no puede aceptarse dos veces dentro de la misma ventana. | Índice `uq_lectura_qr_credencial_ventana_aceptada` |
| RF-03.5 | La dirección puede revocar una credencial y emitir una nueva. | `POST /api/qr/student/<id>/renovar` |

### Módulo de asistencia

| ID | Requisito | Implementación |
|---|---|---|
| RF-04.1 | El docente registra el ingreso escaneando la credencial del estudiante. | `POST /api/attendance/registrar` |
| RF-04.2 | La clasificación en presente, tarde o ausente usa la hora de inicio prevista de la clase y los parámetros de la unidad educativa. | `attendance/services/attendance_rules.py` |
| RF-04.3 | El registro es idempotente: escanear dos veces no genera dos asistencias. | `attendance/services/attendance_service.py` |
| RF-04.4 | El docente puede registrar la asistencia sin escanear el QR. | `POST /api/attendance/sesion/<id>/marcar` |
| RF-04.5 | Cada lectura de QR queda registrada con su resultado y su motivo de rechazo. | Tabla `lecturas_qr` |

### Módulo de justificaciones

| ID | Requisito | Implementación |
|---|---|---|
| RF-05.1 | El tutor solicita la justificación de una ausencia, indicando el rango de fechas y el motivo. | `POST /api/justifications` |
| RF-05.2 | La dirección revisa la justificación y decide si se acepta, se rechaza o se pide más información. | `PUT /api/justifications/<id>/estado` |
| RF-05.3 | Al aceptar una justificación, las asistencias del estudiante en esas quedan marcadas como justificadas. | `justifications/services/justifications_service.py` |

### Módulo de avisos y notificaciones

| ID | Requisito | Implementación |
|---|---|---|
| RF-06.1 | La dirección publica avisos institucionales, eligiendo los roles destinatarios. | `POST /api/announcements` |
| RF-06.2 | Cada usuario ve los avisos publicados para sus roles y puede marcar los leídos. | `PUT /api/announcements/<id>/leer` |
| RF-06.3 | El sistema notifica a los usuarios lo que requiere su atención. | `notifications/` |

### Módulo de seguimiento

| ID | Requisito | Implementación |
|---|---|---|
| RF-07.1 | El sistema detecta ausencias consecutivas, tardanzas repetidas y porcentajes de ausencia excesivos. | `followup/services/pattern_detector.py` |
| RF-07.2 | Las alertas se asignan a un docente y se resuelven con una observación. | `followup/services/followup_service.py` |
| RF-07.3 | La dirección o el docente cita al tutor para revisar un caso. | `meetings/` |

### Módulo de reportes

| ID | Requisito | Implementación |
|---|---|---|
| RF-08.1 | La dirección y los docentes consultan el resumen de asistencia por período y por curso. | `GET /api/reports/resumen` |
| RF-08.2 | El detalle de un estudiante muestra su historial por curso, por mes y sus últimas lecturas. | `GET /api/reports/estudiante/<id>` |

### Módulo de auditoría

| ID | Requisito | Implementación |
|---|---|---|
| RF-09.1 | Las operaciones sensibles quedan registradas con su usuario, su fecha y su detalle. | `audit/services/audit_logger.py` |

## 4. Requisitos no funcionales

| ID | Requisito | Implementación |
|---|---|---|
| RNF-01.1 | El sistema funciona sobre PostgreSQL con el esquema `sesco`. | `app/core/database/base.py` |
| RNF-01.3 | Todas las fechas y horas se manejan en la hora oficial de Bolivia (UTC−4). | `app/core/clock.py` · `config/base.py` |
| RNF-02.2 | Las contraseñas nunca se guardan en texto plano: se usa Argon2. | `core/security/hashing.py` |
| RNF-02.3 | La sesión se cierra tras 15 minutos de inactividad. | `core/security/session_policy.py` |
| RNF-03.1 | La aplicación no expone datos de estudiantes a quien no tiene relación con ellos. | `students/repositories/students_repository.py` (`access_condition`) |
| RNF-03.3 | Todo error indica la causa y la acción a seguir. | `core/errors/messages.py` |
| RNF-04 | Las operaciones que tocan varias tablas se ejecutan en una sola transacción. | `core/database/unit_of_work.py` |
| RNF-05.1 | La interfaz es responsive y accesible por teclado. | `frontend/src/styles/tokens.css` |
| RNF-06.1 | Dar de baja a un estudiante no borra su historial. | `students/services/students_service.py` (`withdraw`) |

## 5. Reglas de datos

| ID | Regla |
|---|---|
| RD-01.3 | Todas las conexiones de la base de datos trabajan con la zona horaria `America/La_Paz`. |
| RD-02.1 | Un estudiante no se muestra si el usuario no tiene relación con él: el mismo 404 se devuelve exista o no. |
| RD-02.2 | El vínculo con un tutor requiere confirmación de la dirección antes de ser visible para el tutor. |

## 6. Modelo de datos

El esquema completo está en `infra/postgres/init.sql` (31 tablas). La vista
`v_asistencia_diaria` consolida por estudiante y fecha los conteos de
asistencia, y es la base de los reportes y de la detección de patrones.

```
unidades_educativas
  - gestores_escolares (gestiones_escolares)
      - cursos - materias - asignaciones_docentes - sesiones_clase
                                                     - asistencias - lecturas_qr
      - configuracion_asistencia

usuarios -+- usuarios_roles - roles
         +- sesiones_usuario
         +- notificaciones
         +- avisos - avisos_destinatarios_roles
         |         - lecturas_avisos
         +- bitacora_auditoria

estudiantes -+- inscripciones - cursos
            +- observaciones_estudiante
            +- estudiante_tutor - tutores
            +- credenciales_qr - lecturas_qr
            +- justificaciones_ausencia
            +- alertas_asistencia - citaciones
            +- registros_salida - autorizaciones_salida
```

## 7. Reglas de la interfaz

| ID | Regla |
|---|---|
| RI-01 | Los errores se muestran con su mensaje y su acción sugerida, nunca con el detalle técnico. |
| RI-02 | Las acciones que no corresponden al rol del usuario no se muestran. |
| RI-03 | Las tablas con muchos registros usan paginación y búsqueda. |
| RI-04 | El lector de QR indica al usuario que falta, se acreditó o se usó dos veces. |
