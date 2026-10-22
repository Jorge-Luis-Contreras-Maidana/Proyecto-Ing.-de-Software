/**
 * Formato de fechas y horas.
 *
 * Toda la aplicación trabaja con la zona horaria de Bolivia (America/La_Paz).
 */

const ZONA_HORARIA = 'America/La_Paz';

const SOLO_FECHA = /^\d{4}-\d{2}-\d{2}$/;
const SOLO_HORA = /^\d{2}:\d{2}(:\d{2})?$/;

const formateadorFecha = new Intl.DateTimeFormat('es-BO', {
  timeZone: ZONA_HORARIA,
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
});

const formateadorFechaCorta = new Intl.DateTimeFormat('es-BO', {
  timeZone: ZONA_HORARIA,
  day: '2-digit',
  month: 'short',
  year: 'numeric',
});

const formateadorHora = new Intl.DateTimeFormat('es-BO', {
  timeZone: ZONA_HORARIA,
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
});

const formateadorFechaHora = new Intl.DateTimeFormat('es-BO', {
  timeZone: ZONA_HORARIA,
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
});

const formateadorIso = new Intl.DateTimeFormat('en-CA', {
  timeZone: ZONA_HORARIA,
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
});

function aFecha(valor: string): Date | null {
  const fecha = new Date(valor);
  return Number.isNaN(fecha.getTime()) ? null : fecha;
}

/** Formatea una fecha como dd/mm/aaaa. */
export function formatearFecha(valor: string | null | undefined): string {
  if (!valor) {
    return '—';
  }
  if (SOLO_FECHA.test(valor)) {
    const [anio, mes, dia] = valor.split('-');
    return `${dia}/${mes}/${anio}`;
  }
  const fecha = aFecha(valor);
  return fecha ? formateadorFecha.format(fecha) : valor;
}

/** Formatea una fecha corta (dd/mes anio). */
export function formatearFechaCorta(valor: string | null | undefined): string {
  if (!valor) {
    return '—';
  }
  if (SOLO_FECHA.test(valor)) {
    const [anio, mes, dia] = valor.split('-');
    return `${dia}/${mes}/${anio}`;
  }
  const fecha = aFecha(valor);
  return fecha ? formateadorFechaCorta.format(fecha) : valor;
}

/** Formatea una hora como hh:mm. */
export function formatearHora(valor: string | null | undefined): string {
  if (!valor) {
    return '—';
  }
  if (SOLO_HORA.test(valor)) {
    return valor.slice(0, 5);
  }
  const fecha = aFecha(valor);
  return fecha ? formateadorHora.format(fecha) : valor;
}

/** Formatea fecha y hora juntas. */
export function formatearFechaHora(valor: string | null | undefined): string {
  if (!valor) {
    return '—';
  }
  if (SOLO_HORA.test(valor)) {
    return valor.slice(0, 5);
  }
  const fecha = aFecha(valor);
  return fecha ? formateadorFechaHora.format(fecha) : valor;
}

/** Fecha de hoy en Bolivia, con el formato yyyy-mm-dd. */
export function fechaActualIso(): string {
  return formateadorIso.format(new Date());
}

/** Convierte una cantidad de segundos en un texto mm:ss. */
export function formatearCuentaAtras(segundos: number): string {
  const total = Math.max(0, Math.floor(segundos));
  const minutos = Math.floor(total / 60);
  const resto = total % 60;
  return `${String(minutos).padStart(2, '0')}:${String(resto).padStart(2, '0')}`;
}

/** Devuelve el valor para un campo de tipo datetime-local, en hora de Bolivia. */
export function aCampoFechaHoraLocal(valor: string | null | undefined): string {
  if (!valor) {
    return '';
  }
  const fecha = aFecha(valor);
  if (!fecha) {
    return '';
  }
  const partes = new Intl.DateTimeFormat('en-CA', {
    timeZone: ZONA_HORARIA,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).formatToParts(fecha);
  const buscar = (tipo: string): string =>
    partes.find((parte) => parte.type === tipo)?.value ?? '00';
  return `${buscar('year')}-${buscar('month')}-${buscar('day')}T${buscar('hour')}:${buscar('minute')}`;
}
