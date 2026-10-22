import { httpClient } from '../../../shared/api/httpClient';
import type { Credencial, CredencialEstudiante, ResultadoVerificacion } from '../types/qr.types';

/** Credencial QR del estudiante con la sesión iniciada. */
export async function obtenerMiCredencial(): Promise<Credencial> {
  const { data } = await httpClient.get<Credencial>('/qr/me/code');
  return data;
}

/** Credencial QR de un estudiante, para el personal de la unidad educativa. */
export async function obtenerCredencialDeEstudiante(idEstudiante: number): Promise<CredencialEstudiante> {
  const { data } = await httpClient.get<CredencialEstudiante>(`/qr/student/${idEstudiante}`);
  return data;
}

/** Emite una credencial nueva para un estudiante. */
export async function renovarCredencial(idEstudiante: number): Promise<Credencial> {
  const { data } = await httpClient.post<Credencial>(`/qr/student/${idEstudiante}/renovar`);
  return data;
}

/** Verifica un código QR sin registrar la asistencia. */
export async function verificarCredencial(
  idEstudiante: number,
  codigo: string
): Promise<ResultadoVerificacion> {
  const { data } = await httpClient.post<ResultadoVerificacion>('/qr/verify', {
    id_estudiante: idEstudiante,
    codigo,
  });
  return data;
}
