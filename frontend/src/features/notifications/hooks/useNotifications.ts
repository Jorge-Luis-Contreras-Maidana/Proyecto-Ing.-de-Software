import { useCallback, useEffect, useState } from 'react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { listarNotificaciones, marcarLeida, marcarTodasLeidas } from '../api/notificationsApi';
import type { Notificacion } from '../types/notifications.types';

export interface ResultadoNotificaciones {
  notificaciones: Notificacion[];
  noLeidas: number;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
  marcarComoLeida: (id: number) => Promise<void>;
  marcarTodas: () => Promise<void>;
  procesando: boolean;
}

/** Carga las notificaciones de la cuenta con sus acciones de lectura. */
export function useNotifications(): ResultadoNotificaciones {
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
  const [noLeidas, setNoLeidas] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    listarNotificaciones()
      .then((respuesta) => {
        if (!vigente) {
          return;
        }
        setNotificaciones(respuesta.items);
        setNoLeidas(respuesta.no_leidas);
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setNotificaciones([]);
          setNoLeidas(0);
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

  const marcarComoLeida = useCallback(async (id: number): Promise<void> => {
    setProcesando(true);
    try {
      await marcarLeida(id);
      setContador((valor) => valor + 1);
    } finally {
      setProcesando(false);
    }
  }, []);

  const marcarTodas = useCallback(async (): Promise<void> => {
    setProcesando(true);
    try {
      await marcarTodasLeidas();
      setContador((valor) => valor + 1);
    } finally {
      setProcesando(false);
    }
  }, []);

  return {
    notificaciones,
    noLeidas,
    cargando,
    error,
    recargar,
    marcarComoLeida,
    marcarTodas,
    procesando,
  };
}
