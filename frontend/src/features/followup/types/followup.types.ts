/** Motivo de la alerta de seguimiento. */
export type TipoAlerta = 'ausencias_consecutivas' | 'tardanzas_reiteradas' | 'porcentaje_ausencia' | 'otra';

/** Estado de la alerta de seguimiento. */
export type EstadoAlerta = 'abierta' | 'en_seguimiento' | 'resuelta' | 'descartada';

/** Alerta de seguimiento sobre un estudiante. */
export interface AlertaSeguimiento {
  id_alerta: number;
  id_estudiante: number;
  id_curso: number;
  tipo: TipoAlerta;
  descripcion: string;
  generada_en: string;
  estado: EstadoAlerta;
  asignada_a: number | null;
  resuelta_en: string | null;
  observacion: string | null;
}

/** Filtros del listado de alertas. */
export interface FiltrosAlerta {
  estado?: EstadoAlerta | null;
  id_estudiante?: number | null;
  id_curso?: number | null;
}

/** Cambio de estado de una alerta. */
export interface CambioEstadoAlerta {
  estado: EstadoAlerta;
  observacion?: string;
}

/** Datos para crear una alerta de forma manual. */
export interface NuevaAlerta {
  id_estudiante: number;
  id_curso: number;
  tipo: TipoAlerta;
  descripcion: string;
  asignada_a?: number;
}

/** Resultado de la detección automática de alertas. */
export interface ResultadoDeteccion {
  items: AlertaSeguimiento[];
  creadas: number;
}
