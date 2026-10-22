import { httpClient } from '../../../shared/api/httpClient';
import type {
  Aviso,
  AvisoInasistenciaDocente,
  FiltrosAviso,
  NuevoAviso,
} from '../types/announcements.types';

/** Lista los avisos institucionales. */
export async function listarAvisos(filtros: FiltrosAviso): Promise<{ items: Aviso[]; total: number }> {
  const { data } = await httpClient.get<{ items: Aviso[]; total: number }>('/announcements', {
    params: {
      estado: filtros.estado ?? undefined,
      solo_no_leidos: filtros.solo_no_leidos ? 'true' : undefined,
    },
  });
  return data;
}

/** Obtiene un aviso por su identificador. */
export async function obtenerAviso(idAviso: number): Promise<Aviso> {
  const { data } = await httpClient.get<Aviso>(`/announcements/${idAviso}`);
  return data;
}

/** Crea un aviso en estado borrador. */
export async function crearAviso(datos: NuevoAviso): Promise<Aviso> {
  const { data } = await httpClient.post<Aviso>('/announcements', datos);
  return data;
}

/** Modifica un aviso existente. */
export async function actualizarAviso(idAviso: number, datos: NuevoAviso): Promise<Aviso> {
  const { data } = await httpClient.put<Aviso>(`/announcements/${idAviso}`, datos);
  return data;
}

/** Publica un aviso para que los destinatarios lo reciban. */
export async function publicarAviso(idAviso: number): Promise<Aviso> {
  const { data } = await httpClient.post<Aviso>(`/announcements/${idAviso}/publicar`);
  return data;
}

/** Marca un aviso como leído por la cuenta. */
export async function marcarAvisoLeido(idAviso: number): Promise<Aviso> {
  const { data } = await httpClient.put<Aviso>(`/announcements/${idAviso}/leer`);
  return data;
}

/** Lista los avisos de inasistencia docente. */
export async function listarInasistenciaDocente(): Promise<AvisoInasistenciaDocente[]> {
  const { data } = await httpClient.get<{ items: AvisoInasistenciaDocente[] }>(
    '/announcements/inasistencia-docente'
  );
  return data.items;
}
