import { useEffect, useState, type FormEvent } from 'react';
import { Save, Settings as SettingsIcon } from 'lucide-react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { formatearFechaHora } from '../../../shared/lib/formatDate';
import { Aviso as AvisoVisual, Encabezado, Tarjeta, Vacio } from '../../../shared/ui';
import { useConfiguracion } from '../hooks/useSettings';
import type { CambiosConfiguracion } from '../types/settings.types';

interface CampoNumerico {
  clave:
    | 'tolerancia_ingreso_min'
    | 'limite_tardanza_min'
    | 'ausencias_consecutivas_alerta'
    | 'tardanzas_mes_alerta'
    | 'porcentaje_ausencia_alerta'
    | 'plazo_justificacion_dias';
  etiqueta: string;
  descripcion: string;
  minimo: number;
  maximo: number;
  paso: number;
}

const CAMPOS: CampoNumerico[] = [
  {
    clave: 'tolerancia_ingreso_min',
    etiqueta: 'Tolerancia de ingreso (minutos)',
    descripcion: 'Ingreso dentro de estos minutos desde el inicio de la clase se cuenta como puntual.',
    minimo: 0,
    maximo: 60,
    paso: 1,
  },
  {
    clave: 'limite_tardanza_min',
    etiqueta: 'Límite de tardanza (minutos)',
    descripcion: 'Pasado este límite desde el inicio, el ingreso se registra como ausencia.',
    minimo: 1,
    maximo: 180,
    paso: 1,
  },
  {
    clave: 'ausencias_consecutivas_alerta',
    etiqueta: 'Ausencias consecutivas para alertar',
    descripcion: 'Número de ausencias seguidas que generan una alerta de seguimiento.',
    minimo: 1,
    maximo: 365,
    paso: 1,
  },
  {
    clave: 'tardanzas_mes_alerta',
    etiqueta: 'Tardanzas en el mes para alertar',
    descripcion: 'Número de tardanzas en un mes que generan una alerta de seguimiento.',
    minimo: 1,
    maximo: 365,
    paso: 1,
  },
  {
    clave: 'porcentaje_ausencia_alerta',
    etiqueta: 'Porcentaje de ausencias para alertar',
    descripcion: 'Porcentaje de ausencias en el período que genera una alerta de seguimiento.',
    minimo: 0,
    maximo: 100,
    paso: 0.5,
  },
  {
    clave: 'plazo_justificacion_dias',
    etiqueta: 'Plazo para justificar (días)',
    descripcion: 'Días desde la ausencia en que el tutor todavía puede solicitar la justificación.',
    minimo: 0,
    maximo: 90,
    paso: 1,
  },
];

/** Parámetros de la unidad educativa que gobiernan la asistencia. */
export function SettingsPage() {
  const { configuracion, cargando, error, guardando, guardar } = useConfiguracion();
  const [valores, setValores] = useState<Record<string, string>>({});
  const [mensaje, setMensaje] = useState<{ tono: 'exito' | 'peligro'; texto: string } | null>(null);

  useEffect(() => {
    if (configuracion) {
      setValores(
        CAMPOS.reduce<Record<string, string>>((acumulado, campo) => {
          acumulado[campo.clave] = String(configuracion[campo.clave]);
          return acumulado;
        }, {})
      );
    }
  }, [configuracion]);

  const enviar = async (evento: FormEvent<HTMLFormElement>): Promise<void> => {
    evento.preventDefault();
    setMensaje(null);
    try {
      const cambios = CAMPOS.reduce<CambiosConfiguracion>((acumulado, campo) => {
        acumulado[campo.clave] = Number(valores[campo.clave]);
        return acumulado;
      }, {});
      await guardar(cambios);
      setMensaje({ tono: 'exito', texto: 'Parámetros guardados correctamente.' });
    } catch (fallo) {
      setMensaje({ tono: 'peligro', texto: obtenerDetalleError(fallo).mensaje });
    }
  };

  if (cargando) {
    return (
      <div className="pagina">
        <Encabezado titulo="Configuración" descripcion="Parámetros de la unidad educativa." />
        <Vacio titulo="Cargando configuración…" />
      </div>
    );
  }

  return (
    <div className="pagina">
      <Encabezado
        titulo="Configuración de la asistencia"
        descripcion="Estos parámetros determinan cómo se clasifica el ingreso de un estudiante y cuándo se generan las alertas."
        icono={<SettingsIcon size={22} aria-hidden="true" />}
      />

      {error ? (
        <AvisoVisual tono="peligro" titulo="No se pudo cargar la configuración">
          {error}
        </AvisoVisual>
      ) : null}

      {mensaje ? (
        <AvisoVisual tono={mensaje.tono === 'exito' ? 'exito' : 'peligro'}>{mensaje.texto}</AvisoVisual>
      ) : null}

      <Tarjeta
        titulo="Parámetros"
        descripcion={
          configuracion?.actualizado_en
            ? `Última actualización: ${formatearFechaHora(configuracion.actualizado_en)}`
            : undefined
        }
      >
        <form className="formulario" onSubmit={enviar}>
          <div className="rejilla rejilla--2">
            {CAMPOS.map((campo) => (
              <div className="campo" key={campo.clave}>
                <label className="campo__etiqueta" htmlFor={campo.clave}>
                  {campo.etiqueta}
                </label>
                <input
                  id={campo.clave}
                  className="entrada"
                  type="number"
                  min={campo.minimo}
                  max={campo.maximo}
                  step={campo.paso}
                  value={valores[campo.clave] ?? ''}
                  onChange={(evento) =>
                    setValores((actuales) => ({ ...actuales, [campo.clave]: evento.target.value }))
                  }
                  required
                />
                <p className="formulario__ayuda">{campo.descripcion}</p>
              </div>
            ))}
          </div>

          <div>
            <button type="submit" className="boton boton--primario" disabled={guardando}>
              <Save size={16} aria-hidden="true" /> {guardando ? 'Guardando…' : 'Guardar parámetros'}
            </button>
          </div>
        </form>
      </Tarjeta>
    </div>
  );
}

export default SettingsPage;
