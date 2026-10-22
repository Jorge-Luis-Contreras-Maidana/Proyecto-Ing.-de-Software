import type { ReactNode } from 'react';
import type { Tono } from '../types/common';

export interface PropiedadesInsignia {
  tono?: Tono;
  children: ReactNode;
}

/** Etiqueta pequeña de color para marcar estados. */
export function Insignia({ tono = 'neutro', children }: PropiedadesInsignia) {
  return <span className={`insignia insignia--${tono}`}>{children}</span>;
}
