import { httpClient } from '../../../shared/api/httpClient';
import type {
  CambioEstadoJustificacion,
  FiltrosJustificacion,
  Justificacion,
  NuevaJustificacion,
} from '../types/justifications.types';

/** Lista las justificaciones de ausencia. */
export async function listarJustificaciones(
  filtros: FiltrosJustificacion
): Promise<{ items: Justificacion[]; total: number }> {
  const { data } = await httpClient.get<{ items: Justificacion[]; total: number }>('/justifications', {
    params: {
      estado: filtros.estado ?? undefined,
      id_estudiante: filtros.id_estudiante ?? undefined,
    },
  });
  return data;
}

/** Obtiene una justificación por su identificador. */
export async function obtenerJustificacion(idJustificacion: number): Promise<Justificacion> {
  const { data } = await httpClient.get<Justificacion>(`/justifications/${idJustificacion}`);
  return data;
}

/** Solicita la justificación de una ausencia. */
export async function crearJustificacion(datos: NuevaJustificacion): Promise<Justificacion> {
  const { data } = await httpClient.post<Justificacion>('/justifications', datos);
  return data;
}

/** Revisa una justificación y decide su estado. */
export async function cambiarEstadoJustificacion(
  idJustificacion: number,
  datos: CambioEstadoJustificacion
): Promise<Justificacion> {
  const { data } = await httpClient.put<Justificacion>(
    `/justifications/${idJustificacion}/estado`,
    datos
  );
  return data;
}
