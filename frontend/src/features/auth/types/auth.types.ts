import type { Rol } from '../../../shared/types/common';

/** Datos del usuario con la sesión iniciada. */
export interface Usuario {
  id_usuario: number;
  nombres: string;
  apellidos: string;
  nombre_usuario: string;
  roles: Rol[];
  debe_cambiar_contrasena?: boolean;
}

/** Perfil devuelto por `GET /api/auth/me`. */
export type PerfilUsuario = Usuario;

/** Credenciales de acceso. */
export interface Credenciales {
  nombre_usuario: string;
  contrasena: string;
}

/** Respuesta del inicio de sesión. */
export interface RespuestaLogin {
  access_token: string;
  inactividad_max_minutos: number;
  usuario: Usuario;
}

/** Respuesta del cierre de sesión. */
export interface RespuestaLogout {
  mensaje: string;
}
