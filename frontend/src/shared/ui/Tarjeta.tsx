import type { ReactNode } from 'react';

export interface PropiedadesTarjeta {
  titulo?: string;
  descripcion?: string;
  acciones?: ReactNode;
  children: ReactNode;
  className?: string;
  sinSeparador?: boolean;
}

/** Contenedor con sombra suave usado para agrupar información. */
export function Tarjeta({
  titulo,
  descripcion,
  acciones,
  children,
  className,
  sinSeparador = false,
}: PropiedadesTarjeta) {
  const clases = ['tarjeta', className].filter(Boolean).join(' ');

  return (
    <section className={clases}>
      {titulo || acciones ? (
        <header className="tarjeta__cabecera">
          <div>
            {titulo ? <h2 className="tarjeta__titulo">{titulo}</h2> : null}
            {descripcion ? <p className="tarjeta__descripcion">{descripcion}</p> : null}
          </div>
          {acciones ? <div className="tarjeta__acciones">{acciones}</div> : null}
        </header>
      ) : null}
      <div className={sinSeparador ? 'tarjeta__cuerpo tarjeta__cuerpo--sinSeparador' : 'tarjeta__cuerpo'}>
        {children}
      </div>
    </section>
  );
}
