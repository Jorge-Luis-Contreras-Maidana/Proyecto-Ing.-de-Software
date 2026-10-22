import { useCallback, useEffect, useState } from 'react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { obtenerCredencialDeEstudiante, obtenerMiCredencial } from '../api/qrApi';
import type { Credencial, CredencialEstudiante } from '../types/qr.types';

export interface ResultadoMiCredencial {
  credencial: Credencial | null;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

/** Carga la credencial QR del estudiante con la sesión iniciada. */
export function useMiCredencial(): ResultadoMiCredencial {
  const [credencial, setCredencial] = useState<Credencial | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    obtenerMiCredencial()
      .then((respuesta) => {
        if (vigente) {
          setCredencial(respuesta);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setCredencial(null);
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

  return { credencial, cargando, error, recargar };
}

export interface ResultadoCredencialEstudiante {
  credencial: CredencialEstudiante | null;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

/** Carga la credencial QR de un estudiante concreto. */
export function useCredencialDeEstudiante(idEstudiante: number | null): ResultadoCredencialEstudiante {
  const [credencial, setCredencial] = useState<CredencialEstudiante | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  useEffect(() => {
    if (idEstudiante === null) {
      setCredencial(null);
      return;
    }

    let vigente = true;
    setCargando(true);
    setError(null);

    obtenerCredencialDeEstudiante(idEstudiante)
      .then((respuesta) => {
        if (vigente) {
          setCredencial(respuesta);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setCredencial(null);
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
  }, [idEstudiante, contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);

  return { credencial, cargando, error, recargar };
}
