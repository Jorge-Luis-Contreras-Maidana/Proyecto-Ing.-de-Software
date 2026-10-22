/** Credencial QR de un estudiante. */
export interface Credencial {
  id_estudiante: number;
  id_credencial: number;
  codigo: string;
  expira_en_segundos: number;
  /** Imagen PNG del código QR en formato base64 (data URL). */
  imagen: string;
}

/** Credencial de un estudiante consultada por el personal. */
export interface CredencialEstudiante extends Credencial {
  nombres: string;
  apellidos: string;
  codigo_estudiante: string;
  estado: string;
  credencial_activa: boolean;
}

/** Resultado de verificar un código QR sin registrar la asistencia. */
export interface ResultadoVerificacion {
  valido: boolean;
  id_estudiante: number;
}
