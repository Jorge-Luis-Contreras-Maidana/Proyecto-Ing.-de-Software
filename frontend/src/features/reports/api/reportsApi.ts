import { httpClient } from '../../../shared/api/httpClient';
import type {
  DetalleEstudiante,
  FilaDiaria,
  FilaReporte,
  FiltrosReporte,
  ResumenReporte,
} from '../types/reports.types';

/** Resumen general de la gestión activa. */
export async function obtenerResumen(): Promise<ResumenReporte> {
  const { data } = await httpClient.get<ResumenReporte>('/reports/resumen');
  return data;
}

/** Reporte de asistencia por estudiante. */
export async function listarAsistencia(
  filtros: FiltrosReporte
): Promise<{ items: FilaReporte[]; total: number }> {
  const { data } = await httpClient.get<{ items: FilaReporte[]; total: number }>('/reports/asistencia', {
    params: {
      desde: filtros.desde ?? undefined,
      hasta: filtros.hasta ?? undefined,
      id_curso: filtros.id_curso ?? undefined,
      id_estudiante: filtros.id_estudiante ?? undefined,
    },
  });
  return data;
}

/** Detalle del reporte de un estudiante. */
export async function obtenerDetalleEstudiante(idEstudiante: number): Promise<DetalleEstudiante> {
  const { data } = await httpClient.get<DetalleEstudiante>(`/reports/estudiante/${idEstudiante}`);
  return data;
}

/** Resumen de un día. */
export async function listarDiario(fecha?: string | null): Promise<{ items: FilaDiaria[]; total: number }> {
  const { data } = await httpClient.get<{ items: FilaDiaria[]; total: number }>('/reports/diario', {
    params: { fecha: fecha ?? undefined },
  });
  return data;
}
