import { httpClient } from '../../../shared/api/httpClient';
import type {
  AlertaSeguimiento,
  CambioEstadoAlerta,
  FiltrosAlerta,
  NuevaAlerta,
  ResultadoDeteccion,
} from '../types/followup.types';

/** Lista las alertas de seguimiento. */
export async function listarAlertas(filtros: FiltrosAlerta): Promise<{
  items: AlertaSeguimiento[];
  total: number;
}> {
  const { data } = await httpClient.get<{ items: AlertaSeguimiento[]; total: number }>(
    '/followup/alertas',
    {
      params: {
        estado: filtros.estado ?? undefined,
        id_estudiante: filtros.id_estudiante ?? undefined,
        id_curso: filtros.id_curso ?? undefined,
      },
    }
  );
  return data;
}

/** Obtiene una alerta de seguimiento. */
export async function obtenerAlerta(idAlerta: number): Promise<AlertaSeguimiento> {
  const { data } = await httpClient.get<AlertaSeguimiento>(`/followup/alertas/${idAlerta}`);
  return data;
}

/** Registra una alerta de seguimiento de forma manual. */
export async function crearAlerta(datos: NuevaAlerta): Promise<AlertaSeguimiento> {
  const { data } = await httpClient.post<AlertaSeguimiento>('/followup/alertas', datos);
  return data;
}

/** Cambia el estado de una alerta de seguimiento. */
export async function cambiarEstadoAlerta(
  idAlerta: number,
  datos: CambioEstadoAlerta
): Promise<AlertaSeguimiento> {
  const { data } = await httpClient.put<AlertaSeguimiento>(`/followup/alertas/${idAlerta}/estado`, {
    estado: datos.estado,
    observacion: datos.observacion ? datos.observacion : undefined,
  });
  return data;
}

/** Ejecuta la detección de alertas según los parámetros de asistencia. */
export async function detectarAlertas(): Promise<ResultadoDeteccion> {
  const { data } = await httpClient.post<ResultadoDeteccion>('/followup/detectar');
  return data;
}

/** Alertas de seguimiento de un estudiante concreto. */
export async function listarAlertasDeEstudiante(
  idEstudiante: number
): Promise<{ items: AlertaSeguimiento[] }> {
  const { data } = await httpClient.get<{ items: AlertaSeguimiento[] }>(
    `/followup/estudiante/${idEstudiante}`
  );
  return data;
}
