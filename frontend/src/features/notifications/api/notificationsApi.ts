import { httpClient } from '../../../shared/api/httpClient';
import type {
  NuevaNotificacion,
  Notificacion,
  RespuestaNotificaciones,
} from '../types/notifications.types';

/** Lista las notificaciones de la cuenta y cuántas hay sin leer. */
export async function listarNotificaciones(): Promise<RespuestaNotificaciones> {
  const { data } = await httpClient.get<RespuestaNotificaciones>('/notifications');
  return data;
}

/** Devuelve solamente cuántas notificaciones hay sin leer. */
export async function contarNoLeidas(): Promise<number> {
  const { data } = await httpClient.get<{ no_leidas: number }>('/notifications/no-leidas');
  return data.no_leidas;
}

/** Marca una notificación como leída. */
export async function marcarLeida(idNotificacion: number): Promise<Notificacion> {
  const { data } = await httpClient.put<Notificacion>(`/notifications/${idNotificacion}/leer`);
  return data;
}

/** Marca como leídas todas las notificaciones de la cuenta. */
export async function marcarTodasLeidas(): Promise<number> {
  const { data } = await httpClient.put<{ actualizadas: number }>('/notifications/leer-todas');
  return data.actualizadas;
}

/** Crea una notificación para una cuenta concreta (solo dirección). */
export async function crearNotificacion(datos: NuevaNotificacion): Promise<Notificacion> {
  const { data } = await httpClient.post<Notificacion>('/notifications', datos);
  return data;
}
