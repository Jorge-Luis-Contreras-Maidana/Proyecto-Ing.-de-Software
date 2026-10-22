# Diagramas de SESCO

Los diagramas están en Mermaid para que se puedan versionar como código. Cualquier
herramienta compatible (GitHub, VS Code con la extensión Mermaid, Obsidian) los
dibuja sin necesidad de exportar imágenes.

| Diagrama | Contenido |
|---|---|
| [`contexto.md`](contexto.md) | El sistema dentro de la unidad educativa y sus actores |
| [`flujo-asistencia-qr.md`](flujo-asistencia-qr.md) | El recorrido completo de un escaneo de QR |
| [`arquitectura.md`](arquitectura.md) | Las capas del backend y cómo se relacionan |

El diccionario de datos (contenido de cada tabla, tipo, longitud y
restricciones) está en el propio esquema: `infra/postgres/init.sql`, y los
modelos que lo mapean se comprueban con `scripts/verificar_modelos.py`.
