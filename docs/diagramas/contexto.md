# Diagrama de contexto

```mermaid
flowchart LR
    subgraph personal["Personal de la unidad educativa"]
        D["Dirección<br/>director"]
        P["Docentes<br/>profesor"]
        T["Tutores<br/>tutor"]
    end

    subgraph comunidad["Comunidad educativa"]
        E["Estudiantes<br/>estudiante"]
        F["Familias<br/>usuarios del tutor"]
    end

    subgraph sistema["SESCO"]
        API["API REST<br/>Flask"]
        BD[("PostgreSQL<br/>esquema sesco")]
        TOTPA["Credenciales TOTP<br/>cifradas"]
    end

    D -->|"configura parámetros<br/>autoriza salidas<br/>revisa justificaciones"| API
    P -->|"registra asistencia<br/>observa estudiantes"| API
    T -->|"solicita justificaciones<br/>consulta sus hijos"| API
    E -->|"muestra su credencial QR"| API
    F -->|"recibe avisos y notificaciones"| API

    API --> BD
    API --> TOTPA
    API -.->|"detección de patrones"| BD
```

## Límites del sistema

- **SESCO** no gestiona la matrícula, la evaluación académica ni la planilla
  docente: solo la asistencia y su seguimiento.
- La **dirección de la unidad educativa** es quien fija los parámetros de
  clasificación (tolerancia y límite de tardanza) y quien autoriza salidas
  anticipadas.
- Los **tutores** ven únicamente a los estudiantes vinculados y confirmados a
  su cargo; el sistema no revela ni siquiera la existencia de los demás.

## Datos de la demostración

Todas las personas, contactos y códigos del conjunto de demostración son
ficticios. Los secretos TOTP de los estudiantes se cifran con la clave
`TOTP_ENCRYPTION_KEY` antes de guardarse, de modo que leer la base de datos no
permite suplantar a ningún estudiante.
