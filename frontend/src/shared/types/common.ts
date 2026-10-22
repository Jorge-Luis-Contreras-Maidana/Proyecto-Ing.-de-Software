/** Tipos compartidos por todos los módulos de la aplicación. */

/** Roles que puede tener una cuenta de usuario. */
export type Rol = 'director' | 'profesor' | 'tutor' | 'estudiante';

/** Respuesta paginada estándar del API. */
export interface Pagina<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

/** Respuesta con una lista simple de elementos. */
export interface ListaSimple<T> {
  items: T[];
  total?: number;
}

/** Respuesta que solo devuelve un mensaje. */
export interface MensajeApi {
  mensaje: string;
}

/** Sobre de error estándar del API. */
export interface SobreErrorApi {
  codigo: string;
  mensaje: string;
  accion: string;
}

/** Tonos visuales usados por las insignias y los avisos. */
export type Tono = 'exito' | 'alerta' | 'peligro' | 'info' | 'neutro';

/** Resultado de una operación que informa al usuario. */
export interface AvisoOperacion {
  tipo: Tono;
  texto: string;
}
