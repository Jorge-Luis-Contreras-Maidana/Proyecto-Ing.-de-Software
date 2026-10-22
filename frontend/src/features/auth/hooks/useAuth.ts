import { createContext, useContext } from 'react';
import type { Credenciales, Usuario } from '../types/auth.types';

/** Valores que expone el proveedor de sesión. */
export interface ValorAutenticacion {
  usuario: Usuario | null;
  token: string | null;
  cargando: boolean;
  estaAutenticado: boolean;
  minutosInactividad: number;
  iniciarSesion: (credenciales: Credenciales) => Promise<void>;
  cerrarSesion: () => Promise<void>;
  refrescarUsuario: () => Promise<void>;
  /** Indica si la cuenta tiene alguno de los roles indicados. */
  tieneRol: (...roles: string[]) => boolean;
}

/** Contexto de la sesión. Lo consume `useAuth` dentro de `AuthProvider`. */
export const ContextoAutenticacion = createContext<ValorAutenticacion | null>(null);

/** Acceso a los datos de la sesión. */
export function useAuth(): ValorAutenticacion {
  const contexto = useContext(ContextoAutenticacion);
  if (!contexto) {
    throw new Error('useAuth debe usarse dentro de AuthProvider.');
  }
  return contexto;
}
