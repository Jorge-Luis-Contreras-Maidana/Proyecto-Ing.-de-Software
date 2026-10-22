/**
 * Configuración de la aplicación leída de las variables de entorno de Vite.
 *
 * Todas las variables se leen aquí para que el resto del código no toque
 * `import.meta.env` directamente.
 */

const variables = import.meta.env as unknown as Record<string, string | boolean | undefined>;

function leerTexto(clave: string, valorAlterno: string): string {
  const valor = variables[clave];
  if (typeof valor === 'string' && valor.trim() !== '') {
    return valor.trim();
  }
  return valorAlterno;
}

function leerBooleano(clave: string, valorAlterno: boolean): boolean {
  const valor = variables[clave];
  if (typeof valor === 'boolean') {
    return valor;
  }
  if (typeof valor === 'string') {
    return valor.trim().toLowerCase() === 'true';
  }
  return valorAlterno;
}

export const configuracion = {
  /** URL base del API. Con "/api" las llamadas pasan por el proxy de Vite. */
  urlApi: leerTexto('VITE_API_URL', '/api'),
  /** Indica si el servidor de desarrollo usa HTTPS (certificado autofirmado). */
  usarSsl: leerBooleano('VITE_USE_SSL', true),
  /** Modo de desarrollo de Vite. */
  esDesarrollo: import.meta.env.DEV,
  /** Nombre visible de la aplicación. */
  nombreAplicacion: 'SESCO',
  /** Nombre completo de la unidad educativa. */
  nombreInstitucion: 'Sistema Escolar de Control y Observación',
} as const;

export type Configuracion = typeof configuracion;
