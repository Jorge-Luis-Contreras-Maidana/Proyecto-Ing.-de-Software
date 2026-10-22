import { httpClient } from '../../../shared/api/httpClient';
import type {
  DetalleSesion,
  FiltrosHistorial,
  HistorialAsistencia,
  RegistroAsistencia,
  RegistroManual,
  RegistroQr,
  SesionClase,
} from '../types/attendance.types';

/** Registra el ingreso de un estudiante escaneando su credencial QR. */
export async function registrarPorQr(datos: RegistroQr): Promise<RegistroAsistencia> {
  const { data } = await httpClient.post<RegistroAsistencia>('/attendance/registrar', {
    id_estudiante: datos.id_estudiante,
    codigo: datos.codigo,
    id_sesion_clase: datos.id_sesion_clase ?? undefined,
  });
  return data;
}

/** Sesiones de clase programadas para hoy. */
export async function listarSesionesDeHoy(): Promise<SesionClase[]> {
  const { data } = await httpClient.get<{ items: SesionClase[] }>('/attendance/hoy');
  return data.items;
}

/** Detalle de una sesión con el estado de cada estudiante. */
export async function obtenerSesion(idSesion: number): Promise<DetalleSesion> {
  const { data } = await httpClient.get<DetalleSesion>(`/attendance/sesion/${idSesion}`);
  return data;
}

/** Registra la asistencia de un estudiante de forma manual. */
export async function marcarManual(idSesion: number, datos: RegistroManual): Promise<RegistroAsistencia> {
  const { data } = await httpClient.post<RegistroAsistencia>(
    `/attendance/sesion/${idSesion}/marcar`,
    {
      id_estudiante: datos.id_estudiante,
      estado: datos.estado,
      observacion: datos.observacion ? datos.observacion : undefined,
    }
  );
  return data;
}

/** Historial de asistencia de un estudiante. */
export async function listarHistorial(
  idEstudiante: number,
  filtros: FiltrosHistorial
): Promise<HistorialAsistencia[]> {
  const { data } = await httpClient.get<{ items: HistorialAsistencia[] }>(
    `/attendance/estudiante/${idEstudiante}`,
    { params: { desde: filtros.desde || undefined, hasta: filtros.hasta || undefined } }
  );
  return data.items;
}
