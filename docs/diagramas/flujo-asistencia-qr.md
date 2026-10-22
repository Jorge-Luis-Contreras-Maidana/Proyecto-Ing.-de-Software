# Flujo de registro de asistencia por QR

## Recorrido de un escaneo

```mermaid
sequenceDiagram
    autonumber
    actor E as Estudiante
    actor P as Docente
    participant V as Frontend
    participant API as API (Flask)
    participant Q as Módulo QR
    participant A as Módulo Asistencia
    participant S as Módulo Settings
    participant BD as PostgreSQL

    E->>V: Abre "Mi QR"
    V->>API: GET /api/qr/me/code
    API->>Q: código_del_estudiante(principal)
    Q->>BD: credencial_qr activa del estudiante
    BD-->>Q: secreto_totp_cifrado
    Q->>Q: descifra y genera el código de la ventana
    Q-->>V: {codigo, expira_en_segundos, imagen (PNG)}

    P->>V: Escanea el QR
    V->>API: POST /api/attendance/registrar {id_estudiante, codigo}
    API->>A: registrar_por_qr(...)
    A->>A: resuelve la sesión de clase (la que está en curso)
    A->>Q: verificar(id_estudiante, codigo)
    Q->>BD: descifra el secreto de E
    Q->>Q: busca la ventana del código (±20 s)
    Q->>BD: ¿ya se aceptó en esa ventana?
    BD-->>Q: no
    Q-->>A: {id_credencial, ventana_totp}
    A->>S: parámetros de la unidad
    S->>BD: configuracion_asistencia
    BD-->>S: tolerancia 5 min, límite 15 min
    A->>A: clasifica: presente / tarde / ausente
    A->>BD: inserta o actualiza la asistencia
    A->>BD: inserta la lectura_qr (aceptada)
    BD-->>A: ok
    A-->>V: {estado, hora_ingreso, minutos_retraso}
    V-->>P: "Presente, 08:02"
```

## Decisiones que protege el sistema

| Amenaza | Defensa | Dónde está |
|---|---|---|
| El QR de un estudiante se usa por otro | Cada estudiante tiene su propio secreto TOTP, cifrado en la base | `qr/services/qr_service.py` |
| Se reenvía la foto del QR | El código cambia cada 20 segundos | `qr/services/totp_service.py` |
| Se reutiliza el mismo código | Una lectura aceptada por credencial y ventana, con índice único | tabla `lecturas_qr` |
| Se registra una asistencia sin clase | La sesión se resuelve por el curso del estudiante y la fecha de hoy | `attendance/services/attendance_service.py` |
| Se falsea la hora de ingreso | Todo el tiempo pasa por `clock.now()` (hora de Bolivia) | `core/clock.py` |
| Se ve un estudiante ajeno | La condición de acceso se aplica en la consulta, no después | `students/repositories/students_repository.py` |
| Se pierde el rastro de una operación | Las operaciones sensibles se registran en `bitacora_auditoria` | `audit/services/audit_logger.py` |

## Caminos de error

| Situación | Respuesta | Mensaje |
|---|---|---|
| Código expirado | 422 | "El código QR expiró o no es válido." |
| Código ya usado en esta ventana | 422 | "Ese código QR ya se usó." |
| El QR es de otro estudiante | 422 | "El código QR expiró o no es válido." (no se revela a quién pertenece) |
| No hay clase programada hoy | 404 | "Hoy no hay ninguna clase programada para este estudiante." |
| El estudiante está retirado | 422 | "El estudiante no está activo." |
| Ya había ingreso en esa clase | 200 | "El ingreso ya estaba registrado para esta clase." |

Los rechazos se guardan en `lecturas_qr` con su motivo, para poder auditar
cuántos intentos fallidos hubo y por qué.
