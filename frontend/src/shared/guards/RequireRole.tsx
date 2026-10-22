import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../features/auth/hooks/useAuth';
import type { Rol } from '../types/common';
import { Cargando } from '../ui';

/** Protege una ruta que exige sesión iniciada. */
export function RequiereSesion({ children }: { children: ReactNode }) {
  const { estaAutenticado, cargando } = useAuth();
  const ubicacion = useLocation();

  if (cargando) {
    return (
      <div className="pagina-carga">
        <Cargando texto="Verificando la sesión…" />
      </div>
    );
  }

  if (!estaAutenticado) {
    return <Navigate to="/login" replace state={{ desde: ubicacion.pathname }} />;
  }

  return <>{children}</>;
}

export interface PropiedadesRequireRole {
  /** Roles con acceso a la ruta. */
  roles: Rol[];
  children: ReactNode;
}

/** Protege una ruta que solo pueden abrir las cuentas con alguno de los roles. */
export function RequireRole({ roles, children }: PropiedadesRequireRole) {
  const { usuario, estaAutenticado, cargando } = useAuth();

  if (cargando) {
    return (
      <div className="pagina-carga">
        <Cargando texto="Verificando la sesión…" />
      </div>
    );
  }

  if (!estaAutenticado) {
    return <Navigate to="/login" replace />;
  }

  if (!usuario || !usuario.roles.some((rol) => roles.includes(rol))) {
    return <Navigate to="/sin-permiso" replace />;
  }

  return <>{children}</>;
}
