# Contrato de la API de SESCO

Todas las rutas cuelgan de `/api`. Salvo `POST /api/auth/login` y
`GET /api/health`, todas exigen un token JWT:
`Authorization: Bearer <access_token>`.

## Formato de los errores

Todo error devuelve el mismo sobre, con un código estable que el frontend
traduce a un mensaje:

```json
{
  "error": {
    "codigo": "datos_invalidos",
    "mensaje": "Los datos enviados no son válidos.",
    "accion": "Revise la información ingresada e intente nuevamente."
  }
}
```

| Código | HTTP | Cuándo |
|---|---|---|
| `credenciales_invalidas` | 401 | Usuario o contraseña incorrectos |
| `no_autenticado` | 401 | Falta el token |
| `token_invalido` | 401 | Token corrupto |
| `sesion_expirada` | 401 | La sesión cerró por inactividad (15 min) |
| `sesion_cerrada` | 401 | La sesión se cerró antes |
| `cuenta_inactiva` | 403 | La cuenta está inactiva o bloqueada |
| `sin_rol` | 403 | La cuenta no tiene rol |
| `sin_permiso` | 403 | El rol no permite la acción |
| `datos_invalidos` | 422 | Validación fallida o regla de negocio |
| `no_encontrado` | 404 | El recurso no existe o no es visible |
| `registro_duplicado` | 409 | Ya existe un registro con esos datos |
| `error_interno` | 500 | Error no controlado |

## Roles

`director`, `profesor`, `tutor`, `estudiante`. Un usuario puede tener varios.

---

## Salud

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| GET | `/api/health` | público | `{"estado": "ok"}` |

## Autenticación

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| POST | `/api/auth/login` | público | `{access_token, inactividad_max_minutos, usuario}` |
| POST | `/api/auth/logout` | autenticado | `{mensaje}` |
| GET | `/api/auth/me` | autenticado | `{id_usuario, nombres, apellidos, nombre_usuario, roles}` |

`usuario` en el login: `{id_usuario, nombres, apellidos, nombre_usuario, roles[], debe_cambiar_contrasena}`.

## Estudiantes

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| GET | `/api/students` | autenticado | `{items[], total, page, per_page}` |
| GET | `/api/students/<id>` | autenticado | estudiante + `tutores[]` |
| POST | `/api/students` | director | 201, estudiante |
| PUT | `/api/students/<id>` | director | estudiante |
| DELETE | `/api/students/<id>` | director | `{mensaje}` |
| GET | `/api/students/<id>/observaciones` | director, profesor | `{items[]}` |
| POST | `/api/students/<id>/observaciones` | director, profesor | 201, observación |
| POST | `/api/students/<id>/tutores` | director | 201, `{mensaje}` |
| POST | `/api/students/<id>/tutores/<id>/confirmar` | director | `{mensaje}` |

Parámetros de `GET /api/students`: `q` (texto, ignora tildes y mayúsculas),
`id_curso`, `estado` (`activo`|`retirado`|`egresado`|`todos`), `page` (≥1),
`per_page` (1–50).

Estudiante: `{id_estudiante, codigo_estudiante, nombres, apellidos,
fecha_nacimiento, genero, estado, curso}`.
`curso`: `{id_curso, nivel, grado, paralelo, turno}` o `null`.

Observación: `{id_observacion, tipo, descripcion, confidencial, registrada_por, fecha_hora}`.
`tipo`: `academica`|`asistencia`|`comportamiento`|`convivencia`|`otra`.

## QR

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| GET | `/api/qr/me/code` | autenticado | credencial propia del estudiante |
| GET | `/api/qr/student/<id>` | director, profesor | credencial + datos del estudiante |
| POST | `/api/qr/verify` | director, profesor | `{valido: true}` |
| POST | `/api/qr/student/<id>/renovar` | director | credencial nueva |

Credencial: `{id_estudiante, id_credencial, codigo, expira_en_segundos, imagen}`.
`imagen` es un `data:image/png;base64,...` con el QR ya generado.

`GET /api/qr/student/<id>` añade `nombres`, `apellidos`, `codigo_estudiante`,
`estado` y `credencial_activa`.

El QR contiene el JSON `{"id_estudiante": 1, "code": "123456", "ventana": 123}`.

## Asistencia

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| POST | `/api/attendance/registrar` | director, profesor | 201 registro |
| GET | `/api/attendance/hoy` | director, profesor | `{items[]}` |
| GET | `/api/attendance/sesion/<id>` | director, profesor | sesión + `estudiantes[]` |
| POST | `/api/attendance/sesion/<id>/marcar` | director, profesor | registro |
| GET | `/api/attendance/estudiante/<id>` | autenticado | `{items[]}` |

`POST /api/attendance/registrar` recibe `{id_estudiante, codigo, id_sesion_clase?}`.
`id_sesion_clase` es opcional: si falta, se elige la clase en curso del estudiante.

Registro: `{id_asistencia, id_sesion_clase, id_estudiante, estado, hora_ingreso,
minutos_retraso, ya_registrado, mensaje}`.
`estado`: `presente`|`tarde`|`ausente`|`justificada`|`pendiente`.

Sesión: `{id_sesion_clase, fecha, hora_inicio_prevista, hora_fin_prevista, estado,
id_curso, curso, turno, id_asignacion, asistencia, estudiantes[]}`.
`asistencia`: `{total, presentes, tardanzas, ausencias, justificadas, pendientes}`.
`estudiantes[]`: `{id_estudiante, nombres, apellidos, codigo_estudiante, estado,
hora_ingreso, metodo_ingreso}`.

`POST /api/attendance/sesion/<id>/marcar` recibe
`{id_estudiante, estado, observacion?}` con `metodo_ingreso = "manual"`.

Historial: `{id_asistencia, id_sesion_clase, fecha, hora_inicio_prevista, estado,
hora_ingreso, metodo_ingreso}`.

## Configuración

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| GET | `/api/settings/attendance` | autenticado | parámetros |
| PUT | `/api/settings/attendance` | director | parámetros |

Parámetros: `{id_configuracion, id_unidad, tolerancia_ingreso_min,
limite_tardanza_min, ausencias_consecutivas_alerta, tardanzas_mes_alerta,
porcentaje_ausencia_alerta, plazo_justificacion_dias, actualizado_en,
actualizado_por}`.

Rangos: tolerancia 0–60, límite 1–180, ausencias 1–365, tardanzas 1–365,
porcentaje 0–100, plazo 0–90.

## Justificaciones

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| GET | `/api/justifications` | director, profesor, tutor | `{items[], total}` |
| GET | `/api/justifications/<id>` | director, profesor, tutor | justificación |
| POST | `/api/justifications` | tutor | 201, justificación |
| PUT | `/api/justifications/<id>/estado` | director | justificación |

Parámetros de `GET`: `estado`, `id_estudiante`.

Justificación: `{id_justificacion, id_estudiante, id_tutor, fecha_inicio, fecha_fin,
motivo, documento_referencia, solicitada_en, estado, revisada_por, revisada_en,
comentario_revision}`.
`estado`: `pendiente`|`avisada`|`justificada`|`no_justificada`|`requiere_informacion`.

`POST` recibe `{id_estudiante, fecha_inicio, fecha_fin, motivo, documento_referencia?}`.
El `id_tutor` se toma de la sesión: el tutor no puede indicar otro.

Al pasar a `justificada`, las asistencias del estudiante en esa fecha quedan
marcadas como `justificada` y enlazadas a la justificación.

## Notificaciones

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| GET | `/api/notifications` | autenticado | `{items[], no_leidas}` |
| GET | `/api/notifications/no-leidas` | autenticado | `{no_leidas}` |
| PUT | `/api/notifications/<id>/leer` | autenticado | notificación |
| PUT | `/api/notifications/leer-todas` | autenticado | `{actualizadas}` |
| POST | `/api/notifications` | director | 201, notificación |

Notificación: `{id_notificacion, tipo, titulo, mensaje, creada_en, entregada_en,
leida_en, estado, entidad_referencia, id_referencia}`.
`tipo`: `ausencia_estudiante`|`tardanza_estudiante`|`salida_estudiante`|
`salida_anticipada`|`citacion`|`aviso`|`otro`.
`estado`: `pendiente`|`entregada`|`leida`|`fallida`.

`POST` recibe `{id_usuario_destinatario, tipo, titulo, mensaje, entidad_referencia?, id_referencia?}`.

## Avisos

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| GET | `/api/announcements` | autenticado | `{items[], total}` |
| GET | `/api/announcements/<id>` | autenticado | aviso |
| POST | `/api/announcements` | director | 201, aviso |
| PUT | `/api/announcements/<id>` | director | aviso |
| POST | `/api/announcements/<id>/publicar` | director | aviso |
| PUT | `/api/announcements/<id>/leer` | autenticado | aviso |
| GET | `/api/announcements/inasistencia-docente` | director, profesor | `{items[]}` |

Parámetros de `GET`: `estado` (`borrador`|`publicado`|`archivado`), `solo_no_leidos`.

Aviso: `{id_aviso, titulo, contenido, creado_por, publicado_en, importante, estado,
roles_destinatarios[], leido, total_lectores}`.
`estado`: `borrador`|`publicado`|`archivado`.

`POST` recibe `{titulo, contenido, importante?, roles_destinatarios?}`.
Si no se indican roles destinatarios, el aviso va para todos.

Aviso de inasistencia docente: `{id_aviso_docente, id_profesor, id_sesion_clase,
fecha_afectada, motivo, enviado_en, estado, revisado_por, revisado_en, decision}`.
`estado`: `pendiente`|`revisado`|`rechazado`|`resuelto`.

## Seguimiento

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| GET | `/api/followup/alertas` | director, profesor, tutor | `{items[], total}` |
| GET | `/api/followup/alertas/<id>` | director, profesor, tutor | alerta |
| POST | `/api/followup/alertas` | director, profesor | 201, alerta |
| PUT | `/api/followup/alertas/<id>/estado` | director, profesor | alerta |
| POST | `/api/followup/detectar` | director | `{items[], creadas}` |
| GET | `/api/followup/estudiante/<id>` | director, profesor, tutor | `{items[]}` |

Parámetros de `GET`: `estado`, `id_estudiante`, `id_curso`.

Alerta: `{id_alerta, id_estudiante, id_curso, tipo, descripcion, generada_en, estado,
asignada_a, resuelta_en, observacion}`.
`tipo`: `ausencias_consecutivas`|`tardanzas_reiteradas`|`porcentaje_ausencia`|`otra`.
`estado`: `abierta`|`en_seguimiento`|`resuelta`|`descartada`.

`POST` recibe `{id_estudiante, id_curso, tipo, descripcion, asignada_a?}`.
`PUT .../estado` recibe `{estado, observacion?}`.

`POST /api/followup/detectar` recorre las asistencias de la gestión activa y
genera alertas según los parámetros de `configuracion_asistencia`
(`ausencias_consecutivas_alerta`, `tardanzas_mes_alerta`,
`porcentaje_ausencia_alerta`). No duplica alertas del mismo tipo y estudiante
que ya estén abiertas.

## Citas

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| GET | `/api/meetings` | director, profesor, tutor | `{items[], total}` |
| GET | `/api/meetings/<id>` | director, profesor, tutor | cita |
| POST | `/api/meetings` | director, profesor | 201, cita |
| PUT | `/api/meetings/<id>/estado` | director, profesor | cita |

Parámetros de `GET`: `estado`, `id_estudiante`.

Cita: `{id_citacion, id_estudiante, id_tutor, id_profesor, id_alerta, fecha_hora,
motivo, estado, creada_en, observaciones}`.
`estado`: `programada`|`confirmada`|`realizada`|`cancelada`|`reprogramada`.

`POST` recibe `{id_estudiante, id_tutor, id_profesor, id_alerta?, fecha_hora, motivo,
observaciones?}`.
`PUT .../estado` recibe `{estado, observaciones?}`.

## Reportes

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| GET | `/api/reports/resumen` | director, profesor | resumen general |
| GET | `/api/reports/asistencia` | director, profesor | `{items[], total}` |
| GET | `/api/reports/estudiante/<id>` | director, profesor, tutor | detalle |
| GET | `/api/reports/diario` | director, profesor | `{items[]}` |

Parámetros: `desde`, `hasta`, `id_curso`, `id_estudiante`.

Resumen: `{total_estudiantes, total_sesiones, presentes, tardanzas, ausencias,
justificadas, pendientes, porcentaje_asistencia, por_curso[]}`.

Detalle de estudiante: `{estudiante, resumen, por_curso[], por_mes[],ULTIMA_lectURA[]}`.

## Auditoría

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| GET | `/api/audit` | director | `{items[], total}` |
| GET | `/api/audit/<id>` | director | evento |

Parámetros: `operacion`, `entidad`, `id_usuario`, `desde`, `hasta`, `page`, `per_page`.

Evento: `{id_evento, id_usuario, operacion, entidad, id_registro, fecha_hora,
direccion_ip, detalle}`.
