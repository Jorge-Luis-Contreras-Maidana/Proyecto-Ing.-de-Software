import { useMemo, useState } from 'react';
import { Bell, CheckCheck } from 'lucide-react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { descripcionEstado } from '../../../shared/lib/etiquetas';
import { formatearFechaHora } from '../../../shared/lib/formatDate';
import { Aviso, Encabezado, Estadistica, Insignia, Tarjeta, Vacio } from '../../../shared/ui';
import { useNotifications } from '../hooks/useNotifications';

/** Bandeja de notificaciones de la cuenta. */
export function NotificationsPage() {
  const {
    notificaciones,
    noLeidas,
    cargando,
    error,
    recargar,
    marcarComoLeida,
    marcarTodas,
    procesando,
  } = useNotifications();

  const [soloNoLeidas, setSoloNoLeidas] = useState(false);
  const [mensaje, setMensaje] = useState<{ tono: 'exito' | 'peligro'; texto: string } | null>(null);

  const visibles = useMemo(
    () => (soloNoLeidas ? notificaciones.filter((notificacion) => !notificacion.leida_en) : notificaciones),
    [notificaciones, soloNoLeidas]
  );

  const manejar = async (accion: () => Promise<void>, mensajeExito: string): Promise<void> => {
    setMensaje(null);
    try {
      await accion();
      setMensaje({ tono: 'exito', texto: mensajeExito });
      recargar();
    } catch (fallo) {
      setMensaje({ tono: 'peligro', texto: obtenerDetalleError(fallo).mensaje });
    }
  };

  return (
    <div className="pagina">
      <Encabezado
        titulo="Notificaciones"
        descripcion="Avisos sobre ausencias, tardanzas y citas de los estudiantes."
        icono={<Bell size={22} aria-hidden="true" />}
        acciones={
          <button
            type="button"
            className="boton boton--secundario"
            onClick={() => void manejar(marcarTodas, 'Se marcaron todas las notificaciones como leídas.')}
            disabled={procesando || noLeidas === 0}
          >
            <CheckCheck size={16} aria-hidden="true" /> Marcar todas como leídas
          </button>
        }
      />

      {mensaje ? (
        <Aviso tono={mensaje.tono === 'exito' ? 'exito' : 'peligro'}>{mensaje.texto}</Aviso>
      ) : null}

      {error ? (
        <Aviso tono="peligro" titulo="No se pudieron cargar las notificaciones">
          {error}
        </Aviso>
      ) : null}

      <div className="rejilla rejilla--3">
        <Estadistica etiqueta="Notificaciones" valor={notificaciones.length} icono={<Bell size={18} aria-hidden="true" />} />
        <Estadistica etiqueta="Sin leer" valor={noLeidas} tono="alerta" />
        <Estadistica
          etiqueta="Leídas"
          valor={Math.max(0, notificaciones.length - noLeidas)}
          tono="exito"
        />
      </div>

      <Tarjeta
        titulo="Bandeja"
        acciones={
          <label className="campo__casilla">
            <input
              type="checkbox"
              checked={soloNoLeidas}
              onChange={(evento) => setSoloNoLeidas(evento.target.checked)}
            />
            Mostrar solo las no leídas
          </label>
        }
      >
        {cargando ? (
          <Vacio titulo="Cargando notificaciones…" />
        ) : visibles.length === 0 ? (
          <Vacio
            titulo="No hay notificaciones"
            descripcion="Cuando haya novedades sobre sus estudiantes aparecerán aquí."
          />
        ) : (
          <ul className="lista-notificaciones">
            {visibles.map((notificacion) => (
              <li
                key={notificacion.id_notificacion}
                className={`lista-notificaciones__item ${notificacion.leida_en ? '' : 'lista-notificaciones__item--nueva'}`}
              >
                <div className="lista-notificaciones__encabezado">
                  <Insignia tono={descripcionEstado(notificacion.tipo).tono}>
                    {descripcionEstado(notificacion.tipo).etiqueta}
                  </Insignia>
                  <span className="lista-notificaciones__fecha">
                    {formatearFechaHora(notificacion.creada_en)}
                  </span>
                </div>
                <p className="lista-notificaciones__titulo">{notificacion.titulo}</p>
                <p className="lista-notificaciones__mensaje">{notificacion.mensaje}</p>
                {!notificacion.leida_en ? (
                  <button
                    type="button"
                    className="boton boton--fantasma boton--pequeno"
                    onClick={() =>
                      void manejar(
                        () => marcarComoLeida(notificacion.id_notificacion),
                        'Notificación marcada como leída.'
                      )
                    }
                    disabled={procesando}
                  >
                    Marcar como leída
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </Tarjeta>
    </div>
  );
}

export default NotificationsPage;
