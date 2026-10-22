import type { ReactNode } from 'react';

export interface PropiedadesEstadistica {
  etiqueta: string;
  valor: ReactNode;
  descripcion?: string;
  icono?: ReactNode;
  tono?: 'exito' | 'alerta' | 'peligro' | 'info' | 'neutro';
}

/** Tarjeta con una cifra destacada. */
export function Estadistica({
  etiqueta,
  valor,
  descripcion,
  icono,
  tono = 'neutro',
}: PropiedadesEstadistica) {
  return (
    <article className={`estadistica estadistica--${tono}`}>
      <div className="estadistica__contenido">
        <p className="estadistica__etiqueta">{etiqueta}</p>
        <p className="estadistica__valor">{valor}</p>
        {descripcion ? <p className="estadistica__descripcion">{descripcion}</p> : null}
      </div>
      {icono ? <span className="estadistica__icono">{icono}</span> : null}
    </article>
  );
}
