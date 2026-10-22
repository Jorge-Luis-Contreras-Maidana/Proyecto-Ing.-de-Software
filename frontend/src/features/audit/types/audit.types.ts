/** Evento registrado en la bitácora de auditoría. */
export interface EventoAuditoria {
  id_evento: number;
  id_usuario: number | null;
  operacion: string;
  entidad: string;
  id_registro: string | null;
  fecha_hora: string;
  direccion_ip: string | null;
  detalle: string | null;
}

/** Filtros del listado de eventos. */
export interface FiltrosAuditoria {
  operacion?: string | null;
  entidad?: string | null;
  id_usuario?: number | null;
  desde?: string | null;
  hasta?: string | null;
  page?: number;
  per_page?: number;
}
