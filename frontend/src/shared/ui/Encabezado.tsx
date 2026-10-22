import type { ReactNode } from 'react';

export interface PropiedadesEncabezado {
  titulo: string;
  descripcion?: string;
  icono?: ReactNode;
  acciones?: ReactNode;
}

/** Encabezado de página con título, descripción y acciones. */
export function Encabezado({ titulo, descripcion, icono, acciones }: PropiedadesEncabezado) {
  return (
    <header className="encabezado">
      <div className="encabezado__texto">
        <h1 className="encabezado__titulo">
          {icono ? <span className="encabezado__icono">{icono}</span> : null}
          {titulo}
        </h1>
        {descripcion ? <p className="encabezado__descripcion">{descripcion}</p> : null}
      </div>
      {acciones ? <div className="encabezado__acciones">{acciones}</div> : null}
    </header>
  );
}
