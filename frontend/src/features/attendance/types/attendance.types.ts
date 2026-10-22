/** Estados posibles de un registro de asistencia. */
export type EstadoAsistencia = 'presente' | 'tarde' | 'ausente' | 'justificada' | 'pendiente';

/** Conteo de estados de una sesión de clase. */
export interface ResumenAsistencia {
  total: number;
  presentes: number;
  tardanzas: number;
  ausencias: number;
  justificadas: number;
  pendientes: number;
}

/** Registro de asistencia de un estudiante en una sesión. */
export interface RegistroAsistencia {
  id_asistencia: number;
  id_sesion_clase: number;
  id_estudiante: number;
  estado: EstadoAsistencia;
  hora_ingreso: string | null;
  minutos_retraso: number;
  ya_registrado: boolean;
  mensaje: string;
}

/** Sesión de clase programada. */
export interface SesionClase {
  id_sesion_clase: number;
  fecha: string;
  hora_inicio_prevista: string;
  hora_fin_prevista: string;
  estado: string;
  id_curso: number;
  curso: string;
  turno: string;
  id_asignacion: number;
  asistencia: ResumenAsistencia;
}

/** Estudiante dentro del detalle de una sesión. */
export interface EstudianteSesion {
  id_estudiante: number;
  nombres: string;
  apellidos: string;
  codigo_estudiante: string;
  estado: EstadoAsistencia;
  hora_ingreso: string | null;
  metodo_ingreso: string | null;
}

/** Detalle de una sesión de clase con la lista de estudiantes. */
export interface DetalleSesion extends SesionClase {
  estudiantes: EstudianteSesion[];
}

/** Registro del historial de asistencia de un estudiante. */
export interface HistorialAsistencia {
  id_asistencia: number;
  id_sesion_clase: number;
  fecha: string;
  hora_inicio_prevista: string;
  estado: EstadoAsistencia;
  hora_ingreso: string | null;
  metodo_ingreso: string | null;
}

/** Datos para registrar el ingreso mediante código QR. */
export interface RegistroQr {
  id_estudiante: number;
  codigo: string;
  id_sesion_clase?: number | null;
}

/** Datos para registrar la asistencia de forma manual. */
export interface RegistroManual {
  id_estudiante: number;
  estado: EstadoAsistencia;
  observacion?: string;
}

/** Filtros del historial de asistencia. */
export interface FiltrosHistorial {
  desde?: string;
  hasta?: string;
}
