import { httpClient } from '../../../shared/api/httpClient';
import type { MensajeApi } from '../../../shared/types/common';
import type {
  ActualizacionEstudiante,
  Estudiante,
  EstudianteDetalle,
  FiltrosEstudiante,
  NuevaObservacion,
  NuevoEstudiante,
  NuevoVinculoTutor,
  Observacion,
  PaginaEstudiantes,
} from '../types/students.types';

/** Lista estudiantes con búsqueda, filtros y paginación. */
export async function listarEstudiantes(filtros: FiltrosEstudiante): Promise<PaginaEstudiantes> {
  const { data } = await httpClient.get<PaginaEstudiantes>('/students', {
    params: {
      q: filtros.q?.trim() ? filtros.q.trim() : undefined,
      id_curso: filtros.id_curso ?? undefined,
      estado: filtros.estado ?? undefined,
      page: filtros.page ?? 1,
      per_page: filtros.per_page ?? 20,
    },
  });
  return data;
}

/** Obtiene un estudiante con sus tutores. */
export async function obtenerEstudiante(idEstudiante: number): Promise<EstudianteDetalle> {
  const { data } = await httpClient.get<EstudianteDetalle>(`/students/${idEstudiante}`);
  return data;
}

/** Registra un estudiante nuevo. */
export async function crearEstudiante(datos: NuevoEstudiante): Promise<Estudiante> {
  const { data } = await httpClient.post<Estudiante>('/students', datos);
  return data;
}

/** Modifica los datos de un estudiante. */
export async function actualizarEstudiante(
  idEstudiante: number,
  datos: ActualizacionEstudiante
): Promise<Estudiante> {
  const { data } = await httpClient.put<Estudiante>(`/students/${idEstudiante}`, datos);
  return data;
}

/** Da de baja a un estudiante (pasa a estado retirado). */
export async function retirarEstudiante(idEstudiante: number): Promise<MensajeApi> {
  const { data } = await httpClient.delete<MensajeApi>(`/students/${idEstudiante}`);
  return data;
}

/** Lista las observaciones registradas de un estudiante. */
export async function listarObservaciones(idEstudiante: number): Promise<{ items: Observacion[] }> {
  const { data } = await httpClient.get<{ items: Observacion[] }>(
    `/students/${idEstudiante}/observaciones`
  );
  return data;
}

/** Registra una observación sobre un estudiante. */
export async function registrarObservacion(
  idEstudiante: number,
  datos: NuevaObservacion
): Promise<Observacion> {
  const { data } = await httpClient.post<Observacion>(
    `/students/${idEstudiante}/observaciones`,
    datos
  );
  return data;
}

/** Vincula un tutor con un estudiante. */
export async function vincularTutor(
  idEstudiante: number,
  datos: NuevoVinculoTutor
): Promise<MensajeApi> {
  const { data } = await httpClient.post<MensajeApi>(`/students/${idEstudiante}/tutores`, datos);
  return data;
}

/** Confirma el vínculo de un tutor con un estudiante. */
export async function confirmarTutor(idEstudiante: number, idTutor: number): Promise<MensajeApi> {
  const { data } = await httpClient.post<MensajeApi>(
    `/students/${idEstudiante}/tutores/${idTutor}/confirmar`
  );
  return data;
}
