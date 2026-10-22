import { useCallback, useEffect, useState } from 'react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { listarAsistencia, listarDiario, obtenerDetalleEstudiante, obtenerResumen } from '../api/reportsApi';
import type {
  DetalleEstudiante,
  FilaDiaria,
  FilaReporte,
  FiltrosReporte,
  ResumenReporte,
} from '../types/reports.types';

export interface ResultadoResumen {
  resumen: ResumenReporte | null;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

/** Carga el resumen general de asistencia. */
export function useResumen(activo = true): ResultadoResumen {
  const [resumen, setResumen] = useState<ResumenReporte | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  useEffect(() => {
    if (!activo) {
      setCargando(false);
      return;
    }
    let vigente = true;
    setCargando(true);
    setError(null);

    obtenerResumen()
      .then((datos) => {
        if (vigente) {
          setResumen(datos);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setResumen(null);
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
  }, [activo, contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);

  return { resumen, cargando, error, recargar };
}

export interface ResultadoReporte {
  filas: FilaReporte[];
  total: number;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

/** Carga el reporte de asistencia por estudiante. */
export function useReporteAsistencia(filtros: FiltrosReporte): ResultadoReporte {
  const [filas, setFilas] = useState<FilaReporte[]>([]);
  const [total, setTotal] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  const { desde, hasta, id_curso, id_estudiante } = filtros;

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    listarAsistencia({ desde, hasta, id_curso, id_estudiante })
      .then((respuesta) => {
        if (vigente) {
          setFilas(respuesta.items);
          setTotal(respuesta.total);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setFilas([]);
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
  }, [desde, hasta, id_curso, id_estudiante, contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);

  return { filas, total, cargando, error, recargar };
}

export interface ResultadoDiario {
  filas: FilaDiaria[];
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

/** Carga el resumen de asistencia de un día. */
export function useReporteDiario(fecha: string | null): ResultadoDiario {
  const [filas, setFilas] = useState<FilaDiaria[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    listarDiario(fecha)
      .then((respuesta) => {
        if (vigente) {
          setFilas(respuesta.items);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setFilas([]);
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
  }, [fecha, contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);

  return { filas, cargando, error, recargar };
}

export interface ResultadoDetalle {
  detalle: DetalleEstudiante | null;
  cargando: boolean;
  error: string | null;
}

/** Carga el detalle del reporte de un estudiante. */
export function useDetalleEstudiante(idEstudiante: number | null): ResultadoDetalle {
  const [detalle, setDetalle] = useState<DetalleEstudiante | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (idEstudiante === null) {
      setDetalle(null);
      return;
    }
    let vigente = true;
    setCargando(true);
    setError(null);

    obtenerDetalleEstudiante(idEstudiante)
      .then((datos) => {
        if (vigente) {
          setDetalle(datos);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setDetalle(null);
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
  }, [idEstudiante]);

  return { detalle, cargando, error };
}
