/** Totales de asistencia de la gestión activa. */
export interface ResumenReporte {
  total_estudiantes: number;
  total_sesiones: number;
  total_clases: number;
  presentes: number;
  tardanzas: number;
  ausencias: number;
  justificadas: number;
  pendientes: number;
  porcentaje_asistencia: number;
  por_curso: ResumenCurso[];
}

/** Totales de un curso concreto. */
export interface ResumenCurso {
  id_curso: number;
  curso: string;
  turno?: string;
  total_clases: number;
  total_sesiones?: number;
  presentes: number;
  tardanzas: number;
  ausencias: number;
  justificadas: number;
  pendientes: number;
  porcentaje_asistencia?: number;
}

/** Fila del reporte de asistencia por estudiante. */
export interface FilaReporte {
  id_estudiante: number;
  codigo_estudiante: string;
  nombres: string;
  apellidos: string;
  id_curso: number | null;
  curso: string | null;
  presentes: number;
  tardanzas: number;
  ausencias: number;
  justificadas: number;
  pendientes: number;
  total_clases: number;
  porcentaje_asistencia: number;
}

/** Filtros del reporte de asistencia. */
export interface FiltrosReporte {
  desde?: string | null;
  hasta?: string | null;
  id_curso?: number | null;
  id_estudiante?: number | null;
}

/** Resumen diario de asistencia (vista v_asistencia_diaria). */
export interface FilaDiaria {
  id_estudiante: number;
  codigo_estudiante: string;
  nombres: string;
  apellidos: string;
  fecha: string;
  total_clases: number;
  presentes: number;
  tardanzas: number;
  ausencias: number;
  justificadas: number;
  pendientes: number;
  primer_ingreso: string | null;
  ultima_salida: string | null;
}

/** Bloque de conteos que comparten el resumen y sus desgloses. */
export interface BloqueConteos {
  total_clases: number;
  presentes: number;
  tardanzas: number;
  ausencias: number;
  justificadas: number;
  pendientes: number;
  porcentaje_asistencia: number;
}

/** Totales de un mes. */
export interface ResumenMes extends BloqueConteos {
  mes: string;
}

/** Últimas asistencias registradas de un estudiante. */
export interface LecturaReporte {
  id_asistencia: number;
  id_sesion_clase: number;
  id_curso: number;
  curso: string;
  fecha: string;
  hora_inicio_prevista: string;
  estado: string;
  hora_ingreso: string | null;
  metodo_ingreso: string | null;
}

/** Detalle del reporte de un estudiante. */
export interface DetalleEstudiante {
  estudiante: {
    id_estudiante: number;
    codigo_estudiante: string;
    nombres: string;
    apellidos: string;
    fecha_nacimiento: string;
    genero: string | null;
    estado: string;
    curso: { id_curso: number; nivel: string; grado: number; paralelo: string; turno: string } | null;
  };
  resumen: BloqueConteos;
  por_curso: ResumenCurso[];
  por_mes: ResumenMes[];
  ultimas_lecturas: LecturaReporte[];
}
