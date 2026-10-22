/** Estado de un aviso institucional. */
export type EstadoAviso = 'borrador' | 'publicado' | 'archivado';

/** Aviso institucional publicado por la dirección. */
export interface Aviso {
  id_aviso: number;
  titulo: string;
  contenido: string;
  creado_por: number;
  publicado_en: string | null;
  importante: boolean;
  estado: EstadoAviso;
  roles_destinatarios: string[];
  leido: boolean;
  total_lectores: number;
}

/** Datos para crear un aviso. */
export interface NuevoAviso {
  titulo: string;
  contenido: string;
  importante?: boolean;
  roles_destinatarios?: string[];
}

/** Filtros del listado de avisos. */
export interface FiltrosAviso {
  estado?: EstadoAviso | null;
  solo_no_leidos?: boolean;
}

/** Estado de un aviso de inasistencia docente. */
export type EstadoAvisoDocente = 'pendiente' | 'revisado' | 'rechazado' | 'resuelto';

/** Aviso generado por la inasistencia de un docente. */
export interface AvisoInasistenciaDocente {
  id_aviso_docente: number;
  id_profesor: number;
  id_sesion_clase: number;
  fecha_afectada: string;
  motivo: string;
  enviado_en: string;
  estado: EstadoAvisoDocente;
  revisado_por: number | null;
  revisado_en: string | null;
  decision: string | null;
}
