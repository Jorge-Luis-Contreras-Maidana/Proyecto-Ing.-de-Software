export interface PropiedadesCargando {
  texto?: string;
}

/** Indicador de carga. */
export function Cargando({ texto = 'Cargando…' }: PropiedadesCargando) {
  return (
    <div className="cargando" role="status" aria-live="polite">
      <span className="cargando__circulo" aria-hidden="true" />
      <span className="cargando__texto">{texto}</span>
    </div>
  );
}
