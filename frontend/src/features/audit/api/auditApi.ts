import { httpClient } from '../../../shared/api/httpClient';
import type { EventoAuditoria, FiltrosAuditoria } from '../types/audit.types';

/** Lista los eventos de la bitácora de auditoría. */
export async function listarEventos(filtros: FiltrosAuditoria): Promise<{
  items: EventoAuditoria[];
  total: number;
}> {
  const { data } = await httpClient.get<{ items: EventoAuditoria[]; total: number }>('/audit', {
    params: {
      operacion: filtros.operacion ?? undefined,
      entidad: filtros.entidad ?? undefined,
      id_usuario: filtros.id_usuario ?? undefined,
      desde: filtros.desde ?? undefined,
      hasta: filtros.hasta ?? undefined,
      page: filtros.page ?? undefined,
      per_page: filtros.per_page ?? undefined,
    },
  });
  return data;
}

/** Obtiene un evento de la bitácora. */
export async function obtenerEvento(idEvento: number): Promise<EventoAuditoria> {
  const { data } = await httpClient.get<EventoAuditoria>(`/audit/${idEvento}`);
  return data;
}
