import { useCallback, useEffect, useState } from 'react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { actualizarConfiguracion, obtenerConfiguracion } from '../api/settingsApi';
import type { CambiosConfiguracion, ConfiguracionAsistencia } from '../types/settings.types';

export interface ResultadoConfiguracion {
  configuracion: ConfiguracionAsistencia | null;
  cargando: boolean;
  error: string | null;
  guardando: boolean;
  recargar: () => void;
  guardar: (cambios: CambiosConfiguracion) => Promise<ConfiguracionAsistencia>;
}

/** Carga los parámetros de asistencia y permite guardarlos. */
export function useConfiguracion(): ResultadoConfiguracion {
  const [configuracion, setConfiguracion] = useState<ConfiguracionAsistencia | null>(null);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    obtenerConfiguracion()
      .then((datos) => {
        if (vigente) {
          setConfiguracion(datos);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setConfiguracion(null);
          setError(obtenerDetalleError(fallo).mensaje);
        }
      })
      .finally(() => {
        if (vigente) {
          setCargando(false);
        }
      });

    return () => {
      vigente = false;
    };
  }, [contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);

  const guardar = useCallback(
    async (cambios: CambiosConfiguracion): Promise<ConfiguracionAsistencia> => {
      setGuardando(true);
      try {
        const actualizada = await actualizarConfiguracion(cambios);
        setConfiguracion(actualizada);
        return actualizada;
      } finally {
        setGuardando(false);
      }
    },
    []
  );

  return { configuracion, cargando, error, guardando, recargar, guardar };
}
