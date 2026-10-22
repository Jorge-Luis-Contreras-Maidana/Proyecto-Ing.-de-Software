/** Estado de una justificación de ausencia. */
export type EstadoJustificacion =
  | 'pendiente'
  | 'avisada'
  | 'justificada'
  | 'no_justificada'
  | 'requiere_informacion';

/** Justificación de una ausencia solicitada por el tutor. */
export interface Justificacion {
  id_justificacion: number;
  id_estudiante: number;
  id_tutor: number;
  fecha_inicio: string;
  fecha_fin: string;
  motivo: string;
  documento_referencia: string | null;
  solicitada_en: string;
  estado: EstadoJustificacion;
  revisada_por: number | null;
  revisada_en: string | null;
  comentario_revision: string | null;
}

/** Filtros del listado de justificaciones. */
export interface FiltrosJustificacion {
  estado?: EstadoJustificacion | null;
  id_estudiante?: number | null;
}

/** Datos para solicitar una justificación. */
export interface NuevaJustificacion {
  id_estudiante: number;
  fecha_inicio: string;
  fecha_fin: string;
  motivo: string;
  documento_referencia?: string;
}

/** Cambio de estado de una justificación. */
export interface CambioEstadoJustificacion {
  estado: EstadoJustificacion;
  comentario?: string;
}
