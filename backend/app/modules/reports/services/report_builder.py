"""Construcción de los reportes de asistencia.

Funciones puras: reciben los datos ya leídos del repositorio y devuelven los
bloques del contrato de API. No usan Flask ni escriben SQL.
"""

# Estados que la aplicación registra en cada clase.
ESTADOS = ("presentes", "tardanzas", "ausencias", "justificadas", "pendientes")


def etiqueta_curso(curso: dict | None) -> str | None:
    """Nombre legible del curso: 'Primaria 4A'."""
    if not curso:
        return None
    grado = curso.get("grado")
    paralelo = curso.get("paralelo")
    return f"{curso.get('nivel')} {grado}{paralelo}"


def porcentaje_asistencia(conteos: dict) -> float:
    """Porcentaje de asistencia del período.

    Se consideran las clases ya registradas (las pendientes no dicen nada del
    estudiante) y se cuentan como asistencia los presentes, las tardanzas y las
    ausencias justificadas.
    """
    evaluadas = (
        conteos.get("presentes", 0)
        + conteos.get("tardanzas", 0)
        + conteos.get("ausencias", 0)
        + conteos.get("justificadas", 0)
    )
    if evaluadas <= 0:
        return 0.0
    asistidas = conteos.get("presentes", 0) + conteos.get("tardanzas", 0) + conteos.get("justificadas", 0)
    return round(asistidas * 100.0 / evaluadas, 2)


def bloque_conteos(conteos: dict) -> dict:
    """Bloque de conteos con su porcentaje de asistencia."""
    datos = {
        "total_clases": int(conteos.get("total_clases", 0)),
        "presentes": int(conteos.get("presentes", 0)),
        "tardanzas": int(conteos.get("tardanzas", 0)),
        "ausencias": int(conteos.get("ausencias", 0)),
        "justificadas": int(conteos.get("justificadas", 0)),
        "pendientes": int(conteos.get("pendientes", 0)),
    }
    datos["porcentaje_asistencia"] = porcentaje_asistencia(datos)
    return datos


def resumen_general(resumen: dict, por_curso: list[dict]) -> dict:
    """Resumen general de la gestión activa."""
    datos = bloque_conteos(resumen)
    datos["total_estudiantes"] = int(resumen.get("total_estudiantes", 0))
    datos["total_sesiones"] = int(resumen.get("total_sesiones", 0))
    datos["por_curso"] = por_curso
    return datos


def bloque_curso_general(conteos: dict, curso: dict | None) -> dict:
    """Bloque por curso del resumen general."""
    datos = bloque_conteos(conteos)
    datos.update(
        {
            "id_curso": conteos["id_curso"],
            "curso": etiqueta_curso(curso),
            "turno": curso.get("turno") if curso else None,
            "total_sesiones": int(conteos.get("total_sesiones", 0)),
        }
    )
    return datos


def fila_asistencia(fila: dict, curso: dict | None) -> dict:
    """Fila del reporte de asistencia: una por estudiante."""
    datos = bloque_conteos(fila)
    datos.update(
        {
            "id_estudiante": fila["id_estudiante"],
            "codigo_estudiante": fila["codigo_estudiante"],
            "nombres": fila["nombres"],
            "apellidos": fila["apellidos"],
            "id_curso": curso.get("id_curso") if curso else None,
            "curso": etiqueta_curso(curso),
        }
    )
    return datos


def bloque_por_curso(conteos_por_curso: list[dict], cursos: dict[int, dict]) -> list[dict]:
    """Desglose por curso del estudiante."""
    bloques = []
    for conteos in conteos_por_curso:
        curso = cursos.get(conteos["id_curso"])
        datos = bloque_conteos(conteos)
        datos.update(
            {
                "id_curso": conteos["id_curso"],
                "curso": etiqueta_curso(curso),
                "nivel": curso.get("nivel") if curso else None,
                "grado": curso.get("grado") if curso else None,
                "paralelo": curso.get("paralelo") if curso else None,
                "turno": curso.get("turno") if curso else None,
            }
        )
        bloques.append(datos)
    return bloques


def bloque_por_mes(conteos_por_mes: list[dict]) -> list[dict]:
    """Desglose por mes del estudiante."""
    return [bloque_conteos(conteos) | {"mes": conteos["mes"]} for conteos in conteos_por_mes]


def bloque_lecturas(lecturas: list[dict], cursos: dict[int, dict]) -> list[dict]:
    """Últimas lecturas de asistencia del estudiante."""
    bloques = []
    for lectura in lecturas:
        curso = cursos.get(lectura["id_curso"])
        bloques.append(
            {
                "id_asistencia": lectura["id_asistencia"],
                "id_sesion_clase": lectura["id_sesion_clase"],
                "id_curso": lectura["id_curso"],
                "curso": etiqueta_curso(curso),
                "fecha": lectura["fecha"].isoformat(),
                "hora_inicio_prevista": lectura["hora_inicio_prevista"].strftime("%H:%M"),
                "estado": lectura["estado"],
                "hora_ingreso": (
                    lectura["hora_ingreso"].isoformat(timespec="seconds")
                    if lectura["hora_ingreso"]
                    else None
                ),
                "metodo_ingreso": lectura["metodo_ingreso"],
            }
        )
    return bloques


def fila_diaria(fila: dict) -> dict:
    """Fila del reporte diario (vista v_asistencia_diaria)."""
    return {
        "id_estudiante": fila["id_estudiante"],
        "codigo_estudiante": fila["codigo_estudiante"],
        "nombres": fila["nombres"],
        "apellidos": fila["apellidos"],
        "fecha": fila["fecha"].isoformat() if hasattr(fila["fecha"], "isoformat") else fila["fecha"],
        "total_clases": int(fila["total_clases"] or 0),
        "presentes": int(fila["presentes"] or 0),
        "tardanzas": int(fila["tardanzas"] or 0),
        "ausencias": int(fila["ausencias"] or 0),
        "justificadas": int(fila["justificadas"] or 0),
        "pendientes": int(fila["pendientes"] or 0),
        "primer_ingreso": (
            fila["primer_ingreso"].isoformat(timespec="seconds") if fila["primer_ingreso"] else None
        ),
        "ultima_salida": (
            fila["ultima_salida"].isoformat(timespec="seconds") if fila["ultima_salida"] else None
        ),
    }
