import { useCallback, useEffect, useState } from 'react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { cambiarEstadoCita, crearCita, listarCitas } from '../api/meetingsApi';
import type { CambioEstadoCita, Cita, FiltrosCita, NuevaCita } from '../types/meetings.types';

export interface ResultadoCitas {
  citas: Cita[];
  total: number;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
  cambiarEstado: (id: number, cambio: CambioEstadoCita) => Promise<void>;
  convocar: (datos: NuevaCita) => Promise<Cita>;
  procesando: boolean;
}

/** Carga las citas de seguimiento con sus acciones. */
export function useCitas(filtros: FiltrosCita): ResultadoCitas {
  const [citas, setCitas] = useState<Cita[]>([]);
  const [total, setTotal] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  const { estado, id_estudiante } = filtros;

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    listarCitas({ estado, id_estudiante })
      .then((respuesta) => {
        if (vigente) {
          setCitas(respuesta.items);
          setTotal(respuesta.total);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setCitas([]);
          setTotal(0);
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
  }, [estado, id_estudiante, contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);

  const cambiarEstado = useCallback(
    async (id: number, cambio: CambioEstadoCita): Promise<void> => {
      setProcesando(true);
      try {
        await cambiarEstadoCita(id, cambio);
        setContador((valor) => valor + 1);
      } finally {
        setProcesando(false);
      }
    },
    []
  );

  const convocar = useCallback(async (datos: NuevaCita): Promise<Cita> => {
    const creada = await crearCita(datos);
    setContador((valor) => valor + 1);
    return creada;
  }, []);

  return { citas, total, cargando, error, recargar, cambiarEstado, convocar, procesando };
}
