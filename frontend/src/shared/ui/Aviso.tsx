import type { ReactNode } from 'react';
import { AlertCircle, CheckCircle2, Info, TriangleAlert } from 'lucide-react';
import type { Tono } from '../types/common';

const ICONOS: Record<Tono, ReactNode> = {
  exito: <CheckCircle2 size={20} aria-hidden="true" />,
  alerta: <TriangleAlert size={20} aria-hidden="true" />,
  peligro: <AlertCircle size={20} aria-hidden="true" />,
  info: <Info size={20} aria-hidden="true" />,
  neutro: <Info size={20} aria-hidden="true" />,
};

export interface PropiedadesAviso {
  tono?: Tono;
  titulo?: string;
  children?: ReactNode;
  accion?: ReactNode;
}

/** Mensaje destacado para informar de errores o resultados. */
export function Aviso({ tono = 'info', titulo, children, accion }: PropiedadesAviso) {
  return (
    <div className={`aviso aviso--${tono}`} role={tono === 'peligro' ? 'alert' : 'status'}>
      <span className="aviso__icono">{ICONOS[tono]}</span>
      <div className="aviso__contenido">
        {titulo ? <strong className="aviso__titulo">{titulo}</strong> : null}
        {children ? <div className="aviso__texto">{children}</div> : null}
      </div>
      {accion ? <div className="aviso__accion">{accion}</div> : null}
    </div>
  );
}
