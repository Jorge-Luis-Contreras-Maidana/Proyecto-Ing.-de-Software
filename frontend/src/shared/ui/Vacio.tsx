import type { ReactNode } from 'react';
import { Inbox } from 'lucide-react';

export interface PropiedadesVacio {
  titulo: string;
  descripcion?: string;
  icono?: ReactNode;
  accion?: ReactNode;
}

/** Estado vacío: se muestra cuando una lista no tiene registros. */
export function Vacio({ titulo, descripcion, icono, accion }: PropiedadesVacio) {
  return (
    <div className="vacio">
      <span className="vacio__icono">{icono ?? <Inbox size={28} aria-hidden="true" />}</span>
      <p className="vacio__titulo">{titulo}</p>
      {descripcion ? <p className="vacio__descripcion">{descripcion}</p> : null}
      {accion ? <div className="vacio__accion">{accion}</div> : null}
    </div>
  );
}
