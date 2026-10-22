import axios, { AxiosHeaders } from 'axios';
import { configuracion } from '../config/env';

/** Clave del token JWT en el almacenamiento local. */
export const CLAVE_TOKEN = 'sesco.token';

/** Clave de los datos del usuario en el almacenamiento local. */
export const CLAVE_USUARIO = 'sesco.usuario';

export const httpClient = axios.create({
  baseURL: configuracion.urlApi,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

/** Devuelve el token guardado, si todavía hay sesión abierta. */
export function leerToken(): string | null {
  return localStorage.getItem(CLAVE_TOKEN);
}

/** Guarda el token de la sesión en curso. */
export function guardarToken(token: string): void {
  localStorage.setItem(CLAVE_TOKEN, token);
}

/** Borra el token y los datos del usuario del almacenamiento local. */
export function limpiarSesion(): void {
  localStorage.removeItem(CLAVE_TOKEN);
  localStorage.removeItem(CLAVE_USUARIO);
}

// Envía el token en todas las peticiones autenticadas.
httpClient.interceptors.request.use((config) => {
  const token = leerToken();
  if (token) {
    const cabeceras = AxiosHeaders.from(config.headers);
    cabeceras.set('Authorization', `Bearer ${token}`);
    config.headers = cabeceras;
  }
  return config;
});

// Cuando el servidor responde 401 la sesión ya no sirve: se limpia y se
// vuelve al formulario de ingreso.
httpClient.interceptors.response.use(
  (respuesta) => respuesta,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      limpiarSesion();
      if (!window.location.pathname.startsWith('/login')) {
        window.location.assign('/login');
      }
    }
    return Promise.reject(error);
  }
);
