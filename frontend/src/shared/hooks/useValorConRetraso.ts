import { useEffect, useState } from 'react';

/**
 * Devuelve el valor después de un momento sin cambios.
 * Se usa en los buscadores para no consultar el API en cada pulsación.
 */
export function useValorConRetraso<T>(valor: T, retraso = 400): T {
  const [valorRetrasado, setValorRetrasado] = useState(valor);

  useEffect(() => {
    const temporizador = window.setTimeout(() => setValorRetrasado(valor), retraso);
    return () => window.clearTimeout(temporizador);
  }, [valor, retraso]);

  return valorRetrasado;
}
