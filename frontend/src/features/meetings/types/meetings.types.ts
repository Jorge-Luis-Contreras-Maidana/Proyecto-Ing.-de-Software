/** Estado de una cita de seguimiento. */
export type EstadoCita = 'programada' | 'confirmada' | 'realizada' | 'cancelada' | 'reprogramada';

/** Cita entre el personal docente y el tutor de un estudiante. */
export interface Cita {
  id_citacion: number;
  id_estudiante: number;
  id_tutor: number;
  id_profesor: number;
  id_alerta: number | null;
  fecha_hora: string;
  motivo: string;
  estado: EstadoCita;
  creada_en: string;
  observaciones: string | null;
}

/** Filtros del listado de citas. */
export interface FiltrosCita {
  estado?: EstadoCita | null;
  id_estudiante?: number | null;
}

/** Datos para convocar una cita. */
export interface NuevaCita {
  id_estudiante: number;
  id_tutor: number;
  id_profesor: number;
  id_alerta?: number;
  fecha_hora: string;
  motivo: string;
  observaciones?: string;
}

/** Cambio de estado de una cita. */
export interface CambioEstadoCita {
  estado: EstadoCita;
  observaciones?: string;
}
