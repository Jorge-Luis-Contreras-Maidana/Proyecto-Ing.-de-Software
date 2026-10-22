/** Utilidades de texto para búsquedas y presentación. */

/** Quita tildes y pasa a minúsculas, para comparar textos. */
export function normalizarTexto(valor: string): string {
  return valor
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();
}

/** Indica si el texto contiene la búsqueda, ignorando tildes y mayúsculas. */
export function coincideTexto(texto: string, busqueda: string): boolean {
  if (busqueda.trim() === '') {
    return true;
  }
  return normalizarTexto(texto).includes(normalizarTexto(busqueda));
}

/** Nombre completo de una persona. */
export function nombreCompleto(nombres: string, apellidos: string): string {
  return `${nombres} ${apellidos}`.trim();
}

/** Iniciales de una persona, para los avatares. */
export function iniciales(nombres: string, apellidos: string): string {
  const primero = nombres.trim().charAt(0);
  const segundo = apellidos.trim().charAt(0);
  return `${primero}${segundo}`.toUpperCase() || '?';
}

/** Convierte un texto en un identificador útil para etiquetas de HTML. */
export function aIdentificador(texto: string): string {
  return normalizarTexto(texto)
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
