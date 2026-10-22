import { useCallback, useEffect, useState } from 'react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import {
  cambiarEstadoAlerta,
  crearAlerta,
  detectarAlertas,
  listarAlertas,
} from '../api/followupApi';
import type {
  AlertaSeguimiento,
  CambioEstadoAlerta,
  FiltrosAlerta,
  NuevaAlerta,
  ResultadoDeteccion,
} from '../types/followup.types';

export interface ResultadoAlertas {
  alertas: AlertaSeguimiento[];
  total: number;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
  cambiarEstado: (id: number, cambio: CambioEstadoAlerta) => Promise<void>;
  registrar: (datos: NuevaAlerta) => Promise<AlertaSeguimiento>;
  procesando: boolean;
}

/** Carga las alertas de seguimiento con sus acciones de estado. */
export function useAlertas(filtros: FiltrosAlerta): ResultadoAlertas {
  const [alertas, setAlertas] = useState<AlertaSeguimiento[]>([]);
  const [total, setTotal] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  const { estado, id_estudiante, id_curso } = filtros;

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    listarAlertas({ estado, id_estudiante, id_curso })
      .then((respuesta) => {
        if (vigente) {
          setAlertas(respuesta.items);
          setTotal(respuesta.total);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setAlertas([]);
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
  }, [estado, id_estudiante, id_curso, contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);

  const cambiarEstado = useCallback(
    async (id: number, cambio: CambioEstadoAlerta): Promise<void> => {
      setProcesando(true);
      try {
        await cambiarEstadoAlerta(id, cambio);
        setContador((valor) => valor + 1);
      } finally {
        setProcesando(false);
      }
    },
    []
  );

  const registrar = useCallback(async (datos: NuevaAlerta): Promise<AlertaSeguimiento> => {
    const creada = await crearAlerta(datos);
    setContador((valor) => valor + 1);
    return creada;
  }, []);

  return { alertas, total, cargando, error, recargar, cambiarEstado, registrar, procesando };
}

export interface ResultadoDeteccionAlertas {
  cargando: boolean;
  error: string | null;
  resultado: ResultadoDeteccion | null;
  detectar: () => Promise<void>;
}

/** Ejecuta la detección automática de alertas de seguimiento. */
export function useDeteccion(): ResultadoDeteccionAlertas {
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<ResultadoDeteccion | null>(null);

  const detectar = useCallback(async (): Promise<void> => {
    setCargando(true);
    setError(null);
    try {
      setResultado(await detectarAlertas());
    } catch (fallo: unknown) {
      setError(obtenerDetalleError(fallo).mensaje);
    } finally {
      setCargando(false);
    }
  }, []);

  return { cargando, error, resultado, detectar };
}
