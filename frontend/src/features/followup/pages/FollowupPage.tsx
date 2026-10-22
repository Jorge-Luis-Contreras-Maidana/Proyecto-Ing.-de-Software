import { useState } from 'react';
import { ShieldCheck, Sparkles } from 'lucide-react';
import { useAuth } from '../../auth/hooks/useAuth';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { descripcionEstado } from '../../../shared/lib/etiquetas';
import { formatearFechaHora } from '../../../shared/lib/formatDate';
import { Aviso as AvisoVisual, Encabezado, Estadistica, Insignia, Tarjeta, Vacio } from '../../../shared/ui';
import { useAlertas, useDeteccion } from '../hooks/useFollowup';
import type { EstadoAlerta } from '../types/followup.types';

const ESTADOS: { valor: EstadoAlerta | ''; etiqueta: string }[] = [
  { valor: '', etiqueta: 'Todas' },
  { valor: 'abierta', etiqueta: 'Abiertas' },
  { valor: 'en_seguimiento', etiqueta: 'En seguimiento' },
  { valor: 'resuelta', etiqueta: 'Resueltas' },
  { valor: 'descartada', etiqueta: 'Descartadas' },
];

/** Seguimiento de los casos que requieren intervención. */
export function FollowupPage() {
  const { tieneRol } = useAuth();
  const [estado, setEstado] = useState<EstadoAlerta | ''>('');
  const { alertas, total, cargando, error, cambiarEstado, procesando } = useAlertas({
    estado: estado === '' ? null : estado,
  });
  const deteccion = useDeteccion();

  const abiertas = alertas.filter((alerta) => alerta.estado === 'abierta').length;
  const enSeguimiento = alertas.filter((alerta) => alerta.estado === 'en_seguimiento').length;
  const resueltas = alertas.filter((alerta) => alerta.estado === 'resuelta').length;

  const resolver = async (id: number): Promise<void> => {
    try {
      await cambiarEstado(id, { estado: 'resuelta', observacion: 'Caso revisado desde el panel.' });
    } catch (fallo) {
      // El mensaje se muestra en el aviso general de la pantalla.
      void obtenerDetalleError(fallo);
    }
  };

  return (
    <div className="pagina">
      <Encabezado
        titulo="Seguimiento"
        descripcion="Alertas de inasistencia y tardanzas que requieren la intervención de la unidad educativa."
        icono={<ShieldCheck size={22} aria-hidden="true" />}
        acciones={
          tieneRol('director') ? (
            <button
              type="button"
              className="boton boton--primario"
              onClick={() => void deteccion.detectar()}
              disabled={deteccion.cargando}
            >
              <Sparkles size={16} aria-hidden="true" />
              {deteccion.cargando ? 'Analizando…' : 'Detectar patrones'}
            </button>
          ) : null
        }
      />

      {error ? (
        <AvisoVisual tono="peligro" titulo="No se pudieron cargar las alertas">
          {error}
        </AvisoVisual>
      ) : null}

      {deteccion.error ? (
        <AvisoVisual tono="peligro" titulo="La detección no pudo completarse">
          {deteccion.error}
        </AvisoVisual>
      ) : null}

      {deteccion.resultado ? (
        <AvisoVisual tono="exito" titulo="Detección completada">
          Se crearon {deteccion.resultado.creadas} alertas nuevas y ya existían{' '}
          {deteccion.resultado.items.length - deteccion.resultado.creadas}.
        </AvisoVisual>
      ) : null}

      <div className="rejilla rejilla--3">
        <Estadistica etiqueta="Alertas" valor={total} icono={<ShieldCheck size={18} aria-hidden="true" />} />
        <Estadistica etiqueta="Abiertas" valor={abiertas} tono="peligro" />
        <Estadistica etiqueta="En seguimiento" valor={enSeguimiento} tono="alerta" />
        <Estadistica etiqueta="Resueltas" valor={resueltas} tono="exito" />
      </div>

      <Tarjeta>
        <div className="filtros">
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="filtro-estado-alerta">
              Estado
            </label>
            <select
              id="filtro-estado-alerta"
              className="entrada"
              value={estado}
              onChange={(evento) => setEstado(evento.target.value as EstadoAlerta | '')}
            >
              {ESTADOS.map((opcion) => (
                <option key={opcion.valor} value={opcion.valor}>
                  {opcion.etiqueta}
                </option>
              ))}
            </select>
          </div>
        </div>

        {cargando ? (
          <Vacio titulo="Cargando alertas…" />
        ) : alertas.length === 0 ? (
          <Vacio
            titulo="No hay alertas"
            descripcion="No se detectaron casos que requieran seguimiento con estos filtros."
          />
        ) : (
          <ul className="lista-avisos">
            {alertas.map((alerta) => (
              <li key={alerta.id_alerta} className="lista-avisos__item">
                <div className="lista-avisos__encabezado">
                  <Insignia tono={descripcionEstado(alerta.estado).tono}>
                    {descripcionEstado(alerta.estado).etiqueta}
                  </Insignia>
                  <Insignia tono="neutro">{descripcionEstado(alerta.tipo).etiqueta}</Insignia>
                  <span className="lista-avisos__fecha">{formatearFechaHora(alerta.generada_en)}</span>
                </div>
                <p className="lista-avisos__titulo">Estudiante {alerta.id_estudiante}</p>
                <p className="lista-avisos__contenido">{alerta.descripcion}</p>
                {alerta.observacion ? (
                  <p className="lista-avisos__pie">Observación: {alerta.observacion}</p>
                ) : null}
                {alerta.estado !== 'resuelta' && alerta.estado !== 'descartada' ? (
                  <div className="lista-avisos__acciones">
                    <button
                      type="button"
                      className="boton boton--secundario boton--pequeno"
                      disabled={procesando}
                      onClick={() => void resolver(alerta.id_alerta)}
                    >
                      Marcar como resuelta
                    </button>
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </Tarjeta>
    </div>
  );
}

export default FollowupPage;
