import axios from 'axios';
import type { SobreErrorApi } from '../types/common';

/** Detalle de un error listo para mostrar al usuario. */
export interface DetalleError {
  codigo: string;
  mensaje: string;
  accion: string;
}

/** Extrae el sobre de error estándar del API si la respuesta lo trae. */
export function extraerSobreError(datos: unknown): SobreErrorApi | null {
  if (typeof datos !== 'object' || datos === null) {
    return null;
  }
  const posible = (datos as { error?: unknown }).error;
  if (typeof posible !== 'object' || posible === null) {
    return null;
  }
  const error = posible as Partial<SobreErrorApi>;
  if (typeof error.mensaje !== 'string' || error.mensaje.trim() === '') {
    return null;
  }
  return {
    codigo: typeof error.codigo === 'string' ? error.codigo : 'desconocido',
    mensaje: error.mensaje,
    accion: typeof error.accion === 'string' ? error.accion : '',
  };
}

/** Traduce cualquier error a un mensaje legible para la persona usuaria. */
export function obtenerDetalleError(error: unknown): DetalleError {
  if (axios.isAxiosError(error)) {
    const sobre = extraerSobreError(error.response?.data);
    if (sobre) {
      return { codigo: sobre.codigo, mensaje: sobre.mensaje, accion: sobre.accion };
    }

    const datos = error.response?.data as { mensaje?: unknown } | undefined;
    if (datos && typeof datos.mensaje === 'string' && datos.mensaje.trim() !== '') {
      return { codigo: 'error_servidor', mensaje: datos.mensaje, accion: '' };
    }

    if (!error.response) {
      return {
        codigo: 'error_red',
        mensaje: 'No se pudo conectar con el servidor.',
        accion: 'Verifique que el servicio esté encendido e intente nuevamente.',
      };
    }

    return {
      codigo: `http_${error.response.status}`,
      mensaje: `El servidor respondió con el código ${error.response.status}.`,
      accion: 'Intente nuevamente en unos minutos.',
    };
  }

  if (error instanceof Error && error.message.trim() !== '') {
    return { codigo: 'inesperado', mensaje: error.message, accion: '' };
  }

  return {
    codigo: 'inesperado',
    mensaje: 'Ocurrió un error inesperado.',
    accion: 'Intente nuevamente.',
  };
}

/** Mensaje listo para mostrar, con la acción sugerida incluida. */
export function obtenerMensajeError(error: unknown): string {
  const detalle = obtenerDetalleError(error);
  return detalle.accion ? `${detalle.mensaje} ${detalle.accion}` : detalle.mensaje;
}
