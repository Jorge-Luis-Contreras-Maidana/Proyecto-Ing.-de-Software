import { useEffect, useRef } from 'react';

/** Eventos que cuentan como actividad de la persona usuaria. */
const EVENTOS_ACTIVIDAD = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart'] as const;

export interface OpcionesAutoLogout {
  /** Minutos de inactividad antes de cerrar la sesión. */
  minutosInactividad?: number;
  /** Minutos antes del cierre en los que se avisa a la persona usuaria. */
  minutosAviso?: number;
  /** Se llama cuando queda poco tiempo para que la sesión se cierre. */
  alAdvertir?: (segundosRestantes: number) => void;
  /** Se llama cuando la sesión se cierra por inactividad. */
  alExpirar: () => void;
  /** Permite desactivar la vigilancia (por ejemplo, en la pantalla de ingreso). */
  activo?: boolean;
}

/**
 * Cierra la sesión cuando la persona usuaria lleva demasiado tiempo sin
 * interactuar. El servidor también caduca la sesión por inactividad; este
 * control solo avisa y devuelve al formulario de ingreso.
 */
export function useAutoLogout({
  minutosInactividad = 15,
  minutosAviso = 1,
  alAdvertir,
  alExpirar,
  activo = true,
}: OpcionesAutoLogout): void {
  const ultimaActividad = useRef<number>(Date.now());
  const avisado = useRef<boolean>(false);
  const referenciaExpirar = useRef(alExpirar);
  const referenciaAdvertir = useRef(alAdvertir);

  referenciaExpirar.current = alExpirar;
  referenciaAdvertir.current = alAdvertir;

  useEffect(() => {
    if (!activo) {
      return;
    }

    const registrarActividad = (): void => {
      ultimaActividad.current = Date.now();
      avisado.current = false;
    };

    EVENTOS_ACTIVIDAD.forEach((evento) => {
      window.addEventListener(evento, registrarActividad, { passive: true });
    });

    const intervalo = window.setInterval(() => {
      const minutosInactivos = (Date.now() - ultimaActividad.current) / 60000;

      if (minutosInactivos >= minutosInactividad) {
        window.clearInterval(intervalo);
        referenciaExpirar.current();
        return;
      }

      if (!avisado.current && minutosInactivos >= minutosInactividad - minutosAviso) {
        avisado.current = true;
        referenciaAdvertir.current?.(Math.round((minutosInactividad - minutosInactivos) * 60));
      }
    }, 10000);

    return () => {
      EVENTOS_ACTIVIDAD.forEach((evento) => {
        window.removeEventListener(evento, registrarActividad);
      });
      window.clearInterval(intervalo);
    };
  }, [activo, minutosInactividad, minutosAviso]);
}
