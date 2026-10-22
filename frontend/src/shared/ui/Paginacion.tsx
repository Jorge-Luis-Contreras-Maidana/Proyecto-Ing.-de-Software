import { ChevronLeft, ChevronRight } from 'lucide-react';

export interface PropiedadesPaginacion {
  pagina: number;
  totalPaginas: number;
  total: number;
  onCambioPagina: (pagina: number) => void;
}

/** Controles para moverse entre las páginas de una lista. */
export function Paginacion({ pagina, totalPaginas, total, onCambioPagina }: PropiedadesPaginacion) {
  if (totalPaginas <= 1) {
    return <p className="paginacion__resumen">{total} registro(s)</p>;
  }

  return (
    <div className="paginacion">
      <p className="paginacion__resumen">
        Página {pagina} de {totalPaginas} · {total} registro(s)
      </p>
      <div className="paginacion__botones">
        <button
          type="button"
          className="boton boton--secundario boton--pequeno"
          onClick={() => onCambioPagina(pagina - 1)}
          disabled={pagina <= 1}
        >
          <ChevronLeft size={16} aria-hidden="true" /> Anterior
        </button>
        <button
          type="button"
          className="boton boton--secundario boton--pequeno"
          onClick={() => onCambioPagina(pagina + 1)}
          disabled={pagina >= totalPaginas}
        >
          Siguiente <ChevronRight size={16} aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
