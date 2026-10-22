import { useCallback, useEffect, useState } from 'react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import {
  cambiarEstadoJustificacion,
  crearJustificacion,
  listarJustificaciones,
} from '../api/justificationsApi';
import type {
  CambioEstadoJustificacion,
  FiltrosJustificacion,
  Justificacion,
  NuevaJustificacion,
} from '../types/justifications.types';

export interface ResultadoJustificaciones {
  justificaciones: Justificacion[];
  total: number;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
  solicitar: (datos: NuevaJustificacion) => Promise<Justificacion>;
  revisar: (id: number, cambio: CambioEstadoJustificacion) => Promise<void>;
  procesando: boolean;
}

/** Carga las justificaciones de ausencia con sus acciones. */
export function useJustificaciones(filtros: FiltrosJustificacion): ResultadoJustificaciones {
  const [justificaciones, setJustificaciones] = useState<Justificacion[]>([]);
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

    listarJustificaciones({ estado, id_estudiante })
      .then((respuesta) => {
        if (vigente) {
          setJustificaciones(respuesta.items);
          setTotal(respuesta.total);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setJustificaciones([]);
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

  const solicitar = useCallback(async (datos: NuevaJustificacion): Promise<Justificacion> => {
    const creada = await crearJustificacion(datos);
    setContador((valor) => valor + 1);
    return creada;
  }, []);

  const revisar = useCallback(
    async (id: number, cambio: CambioEstadoJustificacion): Promise<void> => {
      setProcesando(true);
      try {
        await cambiarEstadoJustificacion(id, cambio);
        setContador((valor) => valor + 1);
      } finally {
        setProcesando(false);
      }
    },
    []
  );

  return { justificaciones, total, cargando, error, recargar, solicitar, revisar, procesando };
}
