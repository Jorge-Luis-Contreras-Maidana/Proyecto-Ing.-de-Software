import { useEffect, type ReactNode } from 'react';
import { X } from 'lucide-react';

export interface PropiedadesVentana {
  abierto: boolean;
  titulo: string;
  descripcion?: string;
  onCerrar: () => void;
  children: ReactNode;
  pie?: ReactNode;
}

/** Ventanaemergente para formularios y confirmaciones. */
export function Ventana({
  abierto,
  titulo,
  descripcion,
  onCerrar,
  children,
  pie,
}: PropiedadesVentana) {
  useEffect(() => {
    if (!abierto) {
      return;
    }
    const alPresionar = (evento: KeyboardEvent): void => {
      if (evento.key === 'Escape') {
        onCerrar();
      }
    };
    document.addEventListener('keydown', alPresionar);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', alPresionar);
      document.body.style.overflow = '';
    };
  }, [abierto, onCerrar]);

  if (!abierto) {
    return null;
  }

  return (
    <div className="ventana" role="dialog" aria-modal="true" aria-label={titulo}>
      <div className="ventana__fondo" onClick={onCerrar} />
      <div className="ventana__panel">
        <header className="ventana__cabecera">
          <div>
            <h2 className="ventana__titulo">{titulo}</h2>
            {descripcion ? <p className="ventana__descripcion">{descripcion}</p> : null}
          </div>
          <button type="button" className="boton boton--icono" onClick={onCerrar} aria-label="Cerrar">
            <X size={18} aria-hidden="true" />
          </button>
        </header>
        <div className="ventana__cuerpo">{children}</div>
        {pie ? <footer className="ventana__pie">{pie}</footer> : null}
      </div>
    </div>
  );
}
