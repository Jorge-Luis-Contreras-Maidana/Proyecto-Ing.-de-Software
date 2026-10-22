import { httpClient } from '../../../shared/api/httpClient';
import type {
  CambioEstadoCita,
  Cita,
  FiltrosCita,
  NuevaCita,
} from '../types/meetings.types';

/** Lista las citas de seguimiento. */
export async function listarCitas(filtros: FiltrosCita): Promise<{ items: Cita[]; total: number }> {
  const { data } = await httpClient.get<{ items: Cita[]; total: number }>('/meetings', {
    params: {
      estado: filtros.estado ?? undefined,
      id_estudiante: filtros.id_estudiante ?? undefined,
    },
  });
  return data;
}

/** Obtiene una cita por su identificador. */
export async function obtenerCita(idCita: number): Promise<Cita> {
  const { data } = await httpClient.get<Cita>(`/meetings/${idCita}`);
  return data;
}

/** Convoca una cita. */
export async function crearCita(datos: NuevaCita): Promise<Cita> {
  const { data } = await httpClient.post<Cita>('/meetings', datos);
  return data;
}

/** Cambia el estado de una cita. */
export async function cambiarEstadoCita(idCita: number, datos: CambioEstadoCita): Promise<Cita> {
  const { data } = await httpClient.put<Cita>(`/meetings/${idCita}/estado`, {
    estado: datos.estado,
    observaciones: datos.observaciones ? datos.observaciones : undefined,
  });
  return data;
}
