/** Tipo de notificación enviada a la cuenta. */
export type TipoNotificacion =
  | 'ausencia_estudiante'
  | 'tardanza_estudiante'
  | 'salida_estudiante'
  | 'salida_anticipada'
  | 'citacion'
  | 'aviso'
  | 'otro';

/** Estado de entrega de una notificación. */
export type EstadoNotificacion = 'pendiente' | 'entregada' | 'leida' | 'fallida';

/** Notificación recibida. */
export interface Notificacion {
  id_notificacion: number;
  tipo: TipoNotificacion;
  titulo: string;
  mensaje: string;
  creada_en: string;
  entregada_en: string | null;
  leida_en: string | null;
  estado: EstadoNotificacion;
  entidad_referencia: string | null;
  id_referencia: number | null;
}

/** Listado de notificaciones con el total de las no leídas. */
export interface RespuestaNotificaciones {
  items: Notificacion[];
  no_leidas: number;
}

/** Datos para crear una notificación (solo dirección). */
export interface NuevaNotificacion {
  id_usuario_destinatario: number;
  tipo: TipoNotificacion;
  titulo: string;
  mensaje: string;
  entidad_referencia?: string;
  id_referencia?: number;
}
