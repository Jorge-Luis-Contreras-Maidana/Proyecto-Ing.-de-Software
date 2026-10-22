import type { ReactNode } from 'react';
import { Cargando } from './Cargando';
import { Vacio } from './Vacio';

export interface ColumnaTabla<T> {
  /** Identificador de la columna. */
  clave: string;
  /** Texto que se muestra en la cabecera. */
  etiqueta: string;
  /** Contenido de la celda. Si no se indica, se muestra el valor de `clave`. */
  render?: (fila: T) => ReactNode;
  alineacion?: 'izquierda' | 'centro' | 'derecha';
}

export interface PropiedadesTabla<T> {
  columnas: ColumnaTabla<T>[];
  filas: T[];
  /** Identificador único de cada fila. */
  claveFila: (fila: T) => string | number;
  mensajeVacio?: string;
  descripcionVacio?: string;
  cargando?: boolean;
}

function valorBruto(fila: unknown, clave: string): string {
  if (typeof fila === 'object' && fila !== null) {
    const valor = (fila as Record<string, unknown>)[clave];
    if (valor === null || valor === undefined) {
      return '—';
    }
    return String(valor);
  }
  return '—';
}

/** Tabla de datos con cabecera, estado vacío y estado de carga. */
/** Traduce la alineación en español al valor de CSS. */
function alineacionCss(alineacion: ColumnaTabla<unknown>['alineacion']): 'left' | 'center' | 'right' {
  if (alineacion === 'centro') {
    return 'center';
  }
  if (alineacion === 'derecha') {
    return 'right';
  }
  return 'left';
}

export function Tabla<T>({
  columnas,
  filas,
  claveFila,
  mensajeVacio = 'No hay registros',
  descripcionVacio,
  cargando = false,
}: PropiedadesTabla<T>) {
  if (cargando) {
    return <Cargando texto="Obteniendo datos…" />;
  }

  if (filas.length === 0) {
    return <Vacio titulo={mensajeVacio} descripcion={descripcionVacio} />;
  }

  return (
    <div className="tabla__envoltura">
      <table className="tabla">
        <thead>
          <tr>
            {columnas.map((columna) => (
              <th key={columna.clave} style={{ textAlign: alineacionCss(columna.alineacion) }}>
                {columna.etiqueta}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((fila) => (
            <tr key={claveFila(fila)}>
              {columnas.map((columna) => (
                <td key={columna.clave} style={{ textAlign: alineacionCss(columna.alineacion) }}>
                  {columna.render ? columna.render(fila) : valorBruto(fila, columna.clave)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
