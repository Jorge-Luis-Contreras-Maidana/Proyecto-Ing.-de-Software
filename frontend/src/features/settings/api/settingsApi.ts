import { httpClient } from '../../../shared/api/httpClient';
import type { CambiosConfiguracion, ConfiguracionAsistencia } from '../types/settings.types';

/** Lee los parámetros de la configuración de asistencia. */
export async function obtenerConfiguracion(): Promise<ConfiguracionAsistencia> {
  const { data } = await httpClient.get<ConfiguracionAsistencia>('/settings/attendance');
  return data;
}

/** Guarda los parámetros de la configuración de asistencia. */
export async function actualizarConfiguracion(
  cambios: CambiosConfiguracion
): Promise<ConfiguracionAsistencia> {
  const { data } = await httpClient.put<ConfiguracionAsistencia>('/settings/attendance', cambios);
  return data;
}
