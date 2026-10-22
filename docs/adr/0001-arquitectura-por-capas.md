# ADR 0001 — Arquitectura por capas

- **Estado:** Aceptado
- **Fecha:** 2026-10-21
- **Ámbito:** Backend de SESCO

## Contexto

SESCO tiene once casos de uso (autenticación, estudiantes, QR, asistencia,
justificaciones, avisos, notificaciones, seguimiento, citas, reportes y
auditoría) que comparten un mismo dominio: la asistencia escolar de una unidad
educativa de La Paz, Bolivia.

Cada caso de uso necesita leer y escribir en la base de datos, aplicar reglas
de negocio, y exponerse por HTTP. Además, hay restricciones transversales que
no dependen del caso de uso: la hora oficial de Bolivia, el cifrado de
contraseñas y de secretos, el control de acceso por rol, el formato de los
errores y el cierre de sesión por inactividad.

El riesgo principal no es el tamaño del sistema, sino que las reglas de
seguridad y de tiempo se apliquen de forma distinta en cada módulo. Ya se
comprobó en la práctica: cuatro módulos usaban `datetime.utcnow()` mientras el
proyecto exigía la hora de Bolivia, y un módulo usaba un secreto TOTP único
para todos los estudiantes.

## Decisión

Adoptar una **arquitectura por capas con módulos independientes**, en la que
cada caso de uso es un módulo autonomouso con cuatro capas internas y las
reglas transversales viven en un núcleo compartido.

```
app/
  core/          # transversal: config, errores, seguridad, base de datos, texto, reloj
  modules/
    <caso_de_uso>/
      api/       # rutas (Flask) y esquemas (Pydantic)
      services/  # reglas de negocio
      repositories/  # acceso a datos
      models/    # mapeo SQLAlchemy
```

### Reglas que se aplican

1. **El núcleo no depende de los módulos.** `app.core` no importa nada de
   `app.modules`. Se verifica automáticamente con `import-linter`
   (`backend/.importlinter`), que forma parte de la integración continua.

2. **Las dependencias apuntan hacia adentro.** `api → services → repositories → models`.
   Un servicio nunca importa Flask ni escribe SQL; un repositorio nunca
   decide nada de negocio.

3. **Los módulos se comunican por la interfaz pública de cada uno.** El módulo
   `auth` expone `auth_required` y `current_principal` desde su `__init__.py`.
   Ningún módulo importa de otro que no sea `auth`.

4. **Todo el tiempo pasa por el reloj del núcleo.** `app.core.clock.now()` es
   la única fuente de la hora actual. Está prohibido `datetime.now()` y
   `datetime.utcnow()`, porque el sistema maneja hora local de Bolivia
   (UTC−4) en columnas `TIMESTAMP` sin zona horaria.

5. **Toda transacción pasa por `unit_of_work()`.** Las operaciones que tocan
   varias tablas se ejecutan en una sola transacción: se guardan todas o
   ninguna.

6. **Todo error es un `AppError` con código, mensaje y acción.** El frontend
   traduce ese código; nunca ve una excepción de Python.

7. **Las reglas transversales tienen un solo dueño.** El hashing está en
   `core/security/hashing.py`, el control de acceso en `core/security/rbac.py`,
   la política de sesión en `core/security/session_policy.py`, el cifrado de
   secretos en `core/security/totp_crypto.py` y la búsqueda sin tildes en
   `core/text/search.py`. Ningún módulo reimplementa estas cosas.

## Consecuencias

### A favor

- Una regla transversal se cambia en un solo lugar. Cambiar el tiempo de
  inactividad es editar una constante; cambiar el cifrado, una función.
- Los módulos se pueden probar por separado y sin servidor.
- El contrato de la API queda explícito en `docs/api.md` y se puede comprobar
  módulo por módulo.
- El import-linter falla la integración continua si alguien introduce una
  dependencia prohibida, de modo que la regla no depende de la disciplina.

### En contra

- Más archivos y más indirección: una operación sencilla atraviesa cuatro
  capas.
- Un caso de uso nuevo obliga a crear cuatro archivos, aunque sean pequeños.
- Los datos que cruzan casos de uso (una asistencia y su justificación) no
  tienen un modelo compartido, así que hay que duplicar algunas columnas o
  cruzar entre repositorios.

### Neutro

- El proyecto sigue siendo un monolito. No seJustifica separar en servicios
  independientes: el volumen es de una unidad educativa y el despliegue es
  local o en una sola máquina.

## Alternativas consideradas

**Monolito por capas técnicas (`models/`, `services/`, `routes/` en la raíz).**
Descartada: con once casos de uso, los archivos de `services/` superarían
facilmente la docena y sería difícil saber qué código pertenece a qué caso de
uso. La estructura por módulo mantiene cada caso de uso en una carpeta.

**Microservicios.** Descartada: la transactionsidad entre la asistencia y su
justificación, y el volumen del sistema, no lo justifican.

**Acceso directo a la base de datos desde las rutas (como en el primer
prototipo).** Descartada: fue la causa de que el módulo de asistencia
consultara la base con SQL crudo, con prefijo de esquema escrito a mano, y de
que el módulo de QR usara un secreto global en vez del de cada estudiante.

## Cómo se verifica

```powershell
cd backend
..\venv\Scripts\python.exe -m pytest -q          # las reglas de negocio, sin servidor
..\venv\Scripts\lint-imports                      # el núcleo no depende de los módulos
..\venv\Scripts\python.exe ..\scripts\verificar_modelos.py   # los modelos coinciden con el esquema
```

La última comprobación compara, tabla por tabla y columna por columna, los
modelos SQLAlchemy con el esquema real de la base de datos. Es la que detectó
que faltaban las columnas `confirmado_por`, `confirmado_en` y `ocupacion` en
la tabla `tutores`.
