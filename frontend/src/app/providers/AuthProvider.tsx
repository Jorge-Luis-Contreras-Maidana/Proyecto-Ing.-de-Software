import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import {
  CLAVE_USUARIO,
  guardarToken,
  leerToken,
  limpiarSesion,
} from '../../shared/api/httpClient';
import { obtenerMensajeError } from '../../shared/api/errorMapper';
import {
  ContextoAutenticacion,
  type ValorAutenticacion,
} from '../../features/auth/hooks/useAuth';
import { cerrarSesion, iniciarSesion, obtenerPerfil } from '../../features/auth/api/authApi';
import type { Credenciales, Usuario } from '../../features/auth/types/auth.types';

const MINUTOS_INACTIVIDAD = 15;

function leerUsuarioGuardado(): Usuario | null {
  const datos = localStorage.getItem(CLAVE_USUARIO);
  if (!datos) {
    return null;
  }
  try {
    return JSON.parse(datos) as Usuario;
  } catch {
    localStorage.removeItem(CLAVE_USUARIO);
    return null;
  }
}

function guardarUsuarioGuardado(usuario: Usuario | null): void {
  if (usuario) {
    localStorage.setItem(CLAVE_USUARIO, JSON.stringify(usuario));
  } else {
    localStorage.removeItem(CLAVE_USUARIO);
  }
}

/** Proveedor de la sesión: mantiene el token y los datos del usuario. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(() => leerUsuarioGuardado());
  const [token, setToken] = useState<string | null>(() => leerToken());
  const [cargando, setCargando] = useState<boolean>(true);
  const [minutosInactividad, setMinutosInactividad] = useState<number>(MINUTOS_INACTIVIDAD);

  // Al abrir la aplicación se comprueba que la sesión guardada siga viva.
  useEffect(() => {
    let vigente = true;

    const validar = async (): Promise<void> => {
      const tokenGuardado = leerToken();
      if (!tokenGuardado) {
        if (vigente) {
          setUsuario(null);
          setToken(null);
          setCargando(false);
        }
        return;
      }

      try {
        const perfil = await obtenerPerfil();
        if (vigente) {
          setUsuario(perfil);
          setToken(tokenGuardado);
          guardarUsuarioGuardado(perfil);
        }
      } catch {
        if (vigente) {
          limpiarSesion();
          setUsuario(null);
          setToken(null);
        }
      } finally {
        if (vigente) {
          setCargando(false);
        }
      }
    };

    void validar();

    return () => {
      vigente = false;
    };
  }, []);

  const iniciar = useCallback(async (credenciales: Credenciales): Promise<void> => {
    const respuesta = await iniciarSesion(credenciales);
    guardarToken(respuesta.access_token);
    guardarUsuarioGuardado(respuesta.usuario);
    setToken(respuesta.access_token);
    setUsuario(respuesta.usuario);
    setMinutosInactividad(respuesta.inactividad_max_minutos || MINUTOS_INACTIVIDAD);
  }, []);

  const salir = useCallback(async (): Promise<void> => {
    try {
      await cerrarSesion();
    } catch {
      // Si el servidor ya no conoce la sesión, el cierre local es suficiente.
    } finally {
      limpiarSesion();
      setToken(null);
      setUsuario(null);
    }
  }, []);

  const refrescar = useCallback(async (): Promise<void> => {
    const tokenGuardado = leerToken();
    if (!tokenGuardado) {
      return;
    }
    try {
      const perfil = await obtenerPerfil();
      setUsuario(perfil);
      guardarUsuarioGuardado(perfil);
    } catch (error) {
      console.warn(obtenerMensajeError(error));
    }
  }, []);

  const tieneRol = useCallback(
    (...roles: string[]): boolean => {
      if (!usuario) {
        return false;
      }
      return usuario.roles.some((rol) => roles.includes(rol));
    },
    [usuario]
  );

  const valor = useMemo<ValorAutenticacion>(
    () => ({
      usuario,
      token,
      cargando,
      estaAutenticado: Boolean(token) && usuario !== null,
      minutosInactividad,
      iniciarSesion: iniciar,
      cerrarSesion: salir,
      refrescarUsuario: refrescar,
      tieneRol,
    }),
    [usuario, token, cargando, minutosInactividad, iniciar, salir, refrescar, tieneRol]
  );

  return <ContextoAutenticacion.Provider value={valor}>{children}</ContextoAutenticacion.Provider>;
}
