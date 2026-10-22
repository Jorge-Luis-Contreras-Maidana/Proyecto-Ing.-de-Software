import { httpClient } from '../../../shared/api/httpClient';
import type {
  Credenciales,
  PerfilUsuario,
  RespuestaLogin,
  RespuestaLogout,
} from '../types/auth.types';

/** Inicia sesión y devuelve el token junto con los datos del usuario. */
export async function iniciarSesion(credenciales: Credenciales): Promise<RespuestaLogin> {
  const { data } = await httpClient.post<RespuestaLogin>('/auth/login', {
    nombre_usuario: credenciales.nombre_usuario,
    contrasena: credenciales.contrasena,
  });
  return data;
}

/** Cierra la sesión en el servidor. */
export async function cerrarSesion(): Promise<RespuestaLogout> {
  const { data } = await httpClient.post<RespuestaLogout>('/auth/logout');
  return data;
}

/** Devuelve los datos del usuario de la sesión en curso. */
export async function obtenerPerfil(): Promise<PerfilUsuario> {
  const { data } = await httpClient.get<PerfilUsuario>('/auth/me');
  return data;
}
