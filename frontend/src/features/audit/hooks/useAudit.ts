import { useCallback, useEffect, useState } from 'react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { listarEventos } from '../api/auditApi';
import type { EventoAuditoria, FiltrosAuditoria } from '../types/audit.types';

export interface ResultadoAuditoria {
  eventos: EventoAuditoria[];
  total: number;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
  irAPagina: (pagina: number) => void;
  pagina: number;
}

/** Carga los eventos de la bitácora de auditoría. */
export function useAuditoria(filtros: FiltrosAuditoria): ResultadoAuditoria {
  const [eventos, setEventos] = useState<EventoAuditoria[]>([]);
  const [total, setTotal] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);
  const [pagina, setPagina] = useState(1);

  const { operacion, entidad, id_usuario, desde, hasta } = filtros;

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    listarEventos({ operacion, entidad, id_usuario, desde, hasta, page: pagina, per_page: 25 })
      .then((respuesta) => {
        if (vigente) {
          setEventos(respuesta.items);
          setTotal(respuesta.total);
        }
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setEventos([]);
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
  }, [operacion, entidad, id_usuario, desde, hasta, pagina, contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);
  const irAPagina = useCallback((nueva: number) => setPagina(nueva), []);

  return { eventos, total, cargando, error, recargar, irAPagina, pagina };
}
