import type { Tono } from '../types/common';

/**
 * Etiquetas en español y color asociado para los estados que usa el sistema.
 * Así la misma palabra se ve igual en todas las pantallas.
 */

export interface DescripcionEstado {
  etiqueta: string;
  tono: Tono;
}

const ETIQUETAS_GENERICAS: Record<string, DescripcionEstado> = {
  activo: { etiqueta: 'Activo', tono: 'exito' },
  retirado: { etiqueta: 'Retirado', tono: 'neutro' },
  egresado: { etiqueta: 'Egresado', tono: 'neutro' },
  todos: { etiqueta: 'Todos', tono: 'neutro' },

  presente: { etiqueta: 'Presente', tono: 'exito' },
  tarde: { etiqueta: 'Tarde', tono: 'alerta' },
  ausente: { etiqueta: 'Ausente', tono: 'peligro' },
  justificada: { etiqueta: 'Justificada', tono: 'info' },
  pendiente: { etiqueta: 'Pendiente', tono: 'neutro' },

  borrador: { etiqueta: 'Borrador', tono: 'neutro' },
  publicado: { etiqueta: 'Publicado', tono: 'exito' },
  archivado: { etiqueta: 'Archivado', tono: 'neutro' },

  leida: { etiqueta: 'Leída', tono: 'neutro' },
  leido: { etiqueta: 'Leído', tono: 'neutro' },
  entregada: { etiqueta: 'Entregada', tono: 'info' },
  fallida: { etiqueta: 'Fallida', tono: 'peligro' },

  avisada: { etiqueta: 'Avisada', tono: 'alerta' },
  no_justificada: { etiqueta: 'No justificada', tono: 'peligro' },
  requiere_informacion: { etiqueta: 'Requiere información', tono: 'alerta' },

  abierta: { etiqueta: 'Abierta', tono: 'peligro' },
  en_seguimiento: { etiqueta: 'En seguimiento', tono: 'alerta' },
  resuelta: { etiqueta: 'Resuelta', tono: 'exito' },
  descartada: { etiqueta: 'Descartada', tono: 'neutro' },

  programada: { etiqueta: 'Programada', tono: 'info' },
  confirmada: { etiqueta: 'Confirmada', tono: 'info' },
  realizada: { etiqueta: 'Realizada', tono: 'exito' },
  cancelada: { etiqueta: 'Cancelada', tono: 'peligro' },
  reprogramada: { etiqueta: 'Reprogramada', tono: 'alerta' },

  academica: { etiqueta: 'Académica', tono: 'info' },
  asistencia: { etiqueta: 'Asistencia', tono: 'alerta' },
  comportamiento: { etiqueta: 'Comportamiento', tono: 'peligro' },
  convivencia: { etiqueta: 'Convivencia', tono: 'exito' },
  otra: { etiqueta: 'Otra', tono: 'neutro' },

  ausencias_consecutivas: { etiqueta: 'Ausencias consecutivas', tono: 'peligro' },
  tardanzas_reiteradas: { etiqueta: 'Tardanzas reiteradas', tono: 'alerta' },
  porcentaje_ausencia: { etiqueta: 'Porcentaje de ausencia', tono: 'peligro' },

  ausencia_estudiante: { etiqueta: 'Ausencia', tono: 'peligro' },
  tardanza_estudiante: { etiqueta: 'Tardanza', tono: 'alerta' },
  salida_estudiante: { etiqueta: 'Salida', tono: 'info' },
  salida_anticipada: { etiqueta: 'Salida anticipada', tono: 'alerta' },
  citacion: { etiqueta: 'Citación', tono: 'info' },
  aviso: { etiqueta: 'Aviso', tono: 'info' },

  qr: { etiqueta: 'Código QR', tono: 'exito' },
  manual: { etiqueta: 'Manual', tono: 'neutro' },
};

/** Devuelve la etiqueta y el color de un estado desconocido del catálogo. */
export function descripcionEstado(estado: string | null | undefined): DescripcionEstado {
  if (!estado) {
    return { etiqueta: '—', tono: 'neutro' };
  }
  const encontrado = ETIQUETAS_GENERICAS[estado];
  if (encontrado) {
    return encontrado;
  }
  return { etiqueta: estado.replace(/_/g, ' '), tono: 'neutro' };
}

/** Etiqueta legible de un estado. */
export function etiquetaEstado(estado: string | null | undefined): string {
  return descripcionEstado(estado).etiqueta;
}
