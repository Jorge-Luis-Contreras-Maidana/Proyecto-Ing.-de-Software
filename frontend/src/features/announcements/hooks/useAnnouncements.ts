import { useCallback, useEffect, useState } from 'react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import {
  listarAvisos,
  listarInasistenciaDocente,
  marcarAvisoLeido,
  publicarAviso,
} from '../api/announcementsApi';
import type { Aviso, AvisoInasistenciaDocente, FiltrosAviso } from '../types/announcements.types';

export interface ResultadoAvisos {
  avisos: Aviso[];
  total: number;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
  marcarLeido: (id: number) => Promise<void>;
  publicar: (id: number) => Promise<void>;
  procesando: boolean;
}

/** Carga los avisos institucionales con sus acciones de lectura y publicación. */
export function useAvisos(filtros: FiltrosAviso): ResultadoAvisos {
  const [avisos, setAvisos] = useState<Aviso[]>([]);
  const [total, setTotal] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  const { estado, solo_no_leidos } = filtros;

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    listarAvisos({ estado, solo_no_leidos })
      .then((respuesta) => {
        if (!vigente) {
          return;
        }
        setAvisos(respuesta.items);
        setTotal(respuesta.total);
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setAvisos([]);
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
  }, [estado, solo_no_leidos, contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);

  const marcarLeido = useCallback(async (id: number): Promise<void> => {
    setProcesando(true);
    try {
      await marcarAvisoLeido(id);
      setContador((valor) => valor + 1);
    } finally {
      setProcesando(false);
    }
  }, []);

  const publicar = useCallback(async (id: number): Promise<void> => {
    setProcesando(true);
    try {
      await publicarAviso(id);
      setContador((valor) => valor + 1);
    } finally {
      setProcesando(false);
    }
  }, []);

  return { avisos, total, cargando, error, recargar, marcarLeido, publicar, procesando };
}

export interface ResultadoInasistenciaDocente {
  avisos: AvisoInasistenciaDocente[];
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

/** Carga los avisos de inasistencia docente. */
export function useInasistenciaDocente(): ResultadoInasistenciaDocente {
  const [avisos, setAvisos] = useState<AvisoInasistenciaDocente[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    listarInasistenciaDocente()
      .then((lista) => {
        if (vigente) {
          setAvisos(lista);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setAvisos([]);
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

  return { avisos, cargando, error, recargar };
}
