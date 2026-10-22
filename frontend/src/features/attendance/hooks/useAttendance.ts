import { useCallback, useEffect, useState } from 'react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { listarHistorial, listarSesionesDeHoy, obtenerSesion } from '../api/attendanceApi';
import type {
  DetalleSesion,
  FiltrosHistorial,
  HistorialAsistencia,
  SesionClase,
} from '../types/attendance.types';

export interface ResultadoSesionesHoy {
  sesiones: SesionClase[];
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

/** Carga las sesiones de clase de hoy. */
export function useSesionesDeHoy(): ResultadoSesionesHoy {
  const [sesiones, setSesiones] = useState<SesionClase[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    listarSesionesDeHoy()
      .then((lista) => {
        if (vigente) {
          setSesiones(lista);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setSesiones([]);
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

  return { sesiones, cargando, error, recargar };
}

export interface ResultadoDetalleSesion {
  sesion: DetalleSesion | null;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

/** Carga el detalle de una sesión de clase. */
export function useDetalleSesion(idSesion: number | null): ResultadoDetalleSesion {
  const [sesion, setSesion] = useState<DetalleSesion | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  useEffect(() => {
    if (idSesion === null) {
      setSesion(null);
      return;
    }

    let vigente = true;
    setCargando(true);
    setError(null);

    obtenerSesion(idSesion)
      .then((detalle) => {
        if (vigente) {
          setSesion(detalle);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setSesion(null);
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
  }, [idSesion, contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);

  return { sesion, cargando, error, recargar };
}

export interface ResultadoHistorial {
  historial: HistorialAsistencia[];
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

/** Carga el historial de asistencia de un estudiante. */
export function useHistorial(
  idEstudiante: number | null,
  filtros: FiltrosHistorial
): ResultadoHistorial {
  const [historial, setHistorial] = useState<HistorialAsistencia[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  const { desde, hasta } = filtros;

  useEffect(() => {
    if (idEstudiante === null) {
      setHistorial([]);
      return;
    }

    let vigente = true;
    setCargando(true);
    setError(null);

    listarHistorial(idEstudiante, { desde, hasta })
      .then((lista) => {
        if (vigente) {
          setHistorial(lista);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setHistorial([]);
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
  }, [idEstudiante, desde, hasta, contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);

  return { historial, cargando, error, recargar };
}
