import type { Pagina } from '../../../shared/types/common';

/** Estado de un estudiante dentro de la unidad educativa. */
export type EstadoEstudiante = 'activo' | 'retirado' | 'egresado';

/** Curso al que está inscrito el estudiante. */
export interface Curso {
  id_curso: number;
  nivel: string;
  grado: number;
  paralelo: string;
  turno: string;
}

/** Estudiante registrado en el sistema. */
export interface Estudiante {
  id_estudiante: number;
  codigo_estudiante: string;
  nombres: string;
  apellidos: string;
  fecha_nacimiento: string;
  genero: string | null;
  estado: EstadoEstudiante;
  curso: Curso | null;
}

/** Tutor vinculado a un estudiante. */
export interface TutorVinculado {
  id_tutor: number;
  nombre: string;
  parentesco: string;
  es_contacto_principal: boolean;
  confirmado: boolean;
}

/** Estudiante con el detalle de sus tutores. */
export interface EstudianteDetalle extends Estudiante {
  tutores: TutorVinculado[];
}

/** Tipo de observación sobre el comportamiento o el rendimiento. */
export type TipoObservacion = 'academica' | 'asistencia' | 'comportamiento' | 'convivencia' | 'otra';

/** Observación registrada sobre un estudiante. */
export interface Observacion {
  id_observacion: number;
  tipo: TipoObservacion;
  descripcion: string;
  confidencial: boolean;
  registrada_por: number;
  fecha_hora: string;
}

/** Filtros del listado de estudiantes. */
export interface FiltrosEstudiante {
  q?: string;
  id_curso?: number | null;
  estado?: EstadoEstudiante | 'todos';
  page?: number;
  per_page?: number;
}

/** Datos para registrar un estudiante nuevo. */
export interface NuevoEstudiante {
  codigo_estudiante: string;
  nombres: string;
  apellidos: string;
  fecha_nacimiento: string;
  genero?: string | null;
  id_curso: number;
}

/** Datos que se pueden modificar de un estudiante. */
export interface ActualizacionEstudiante {
  nombres?: string;
  apellidos?: string;
  fecha_nacimiento?: string;
  genero?: string | null;
  id_curso?: number;
}

/** Datos de una observación nueva. */
export interface NuevaObservacion {
  tipo: TipoObservacion;
  descripcion: string;
  confidencial: boolean;
}

/** Datos para vincular un tutor con un estudiante. */
export interface NuevoVinculoTutor {
  id_tutor: number;
  parentesco: string;
  es_contacto_principal: boolean;
}

/** Lista paginada de estudiantes. */
export type PaginaEstudiantes = Pagina<Estudiante>;
