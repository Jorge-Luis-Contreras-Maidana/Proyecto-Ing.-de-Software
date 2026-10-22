import { useState, type FormEvent } from 'react';
import { ClipboardList, FilePlus2 } from 'lucide-react';
import { useAuth } from '../../auth/hooks/useAuth';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { descripcionEstado } from '../../../shared/lib/etiquetas';
import { formatearFecha, formatearFechaHora } from '../../../shared/lib/formatDate';
import { Aviso as AvisoVisual, Encabezado, Estadistica, Insignia, Tarjeta, Vacio, Ventana } from '../../../shared/ui';
import { useJustificaciones } from '../hooks/useJustifications';
import type { EstadoJustificacion, Justificacion, NuevaJustificacion } from '../types/justifications.types';

const ESTADOS: { valor: EstadoJustificacion | ''; etiqueta: string }[] = [
  { valor: '', etiqueta: 'Todas' },
  { valor: 'pendiente', etiqueta: 'Pendientes' },
  { valor: 'avisada', etiqueta: 'Avisadas' },
  { valor: 'justificada', etiqueta: 'Justificadas' },
  { valor: 'no_justificada', etiqueta: 'No justificadas' },
  { valor: 'requiere_informacion', etiqueta: 'Requieren información' },
];

/** Justificaciones de ausencia de los estudiantes. */
export function JustificationsPage() {
  const { tieneRol } = useAuth();
  const esDirector = tieneRol('director');
  const esTutor = tieneRol('tutor');

  const [estado, setEstado] = useState<EstadoJustificacion | ''>('');
  const { justificaciones, total, cargando, error, recargar, solicitar, revisar, procesando } = useJustificaciones({
    estado: estado === '' ? null : estado,
  });
  const [formularioAbierto, setFormularioAbierto] = useState(false);
  const [mensaje, setMensaje] = useState<{ tono: 'exito' | 'peligro'; texto: string } | null>(null);

  const pendientes = justificaciones.filter((j) => j.estado === 'pendiente').length;
  const justificadas = justificaciones.filter((j) => j.estado === 'justificada').length;

  const decidir = async (
    id: number,
    nuevoEstado: EstadoJustificacion,
    comentario: string
  ): Promise<void> => {
    setMensaje(null);
    try {
      await revisar(id, { estado: nuevoEstado, comentario });
      setMensaje({ tono: 'exito', texto: 'Justificación revisada.' });
      recargar();
    } catch (fallo) {
      setMensaje({ tono: 'peligro', texto: obtenerDetalleError(fallo).mensaje });
    }
  };

  return (
    <div className="pagina">
      <Encabezado
        titulo="Justificaciones"
        descripcion="Solicitudes de Justificación de ausencia que el tutor presenta y la dirección revisa."
        icono={<ClipboardList size={22} aria-hidden="true" />}
        acciones={
          esTutor ? (
            <button type="button" className="boton boton--primario" onClick={() => setFormularioAbierto(true)}>
              <FilePlus2 size={16} aria-hidden="true" /> Nueva justificación
            </button>
          ) : null
        }
      />

      {mensaje ? (
        <AvisoVisual tono={mensaje.tono === 'exito' ? 'exito' : 'peligro'}>{mensaje.texto}</AvisoVisual>
      ) : null}

      {error ? (
        <AvisoVisual tono="peligro" titulo="No se pudieron cargar las justificaciones">
          {error}
        </AvisoVisual>
      ) : null}

      <div className="rejilla rejilla--3">
        <Estadistica etiqueta="Justificaciones" valor={total} icono={<ClipboardList size={18} aria-hidden="true" />} />
        <Estadistica etiqueta="Pendientes" valor={pendientes} tono="alerta" />
        <Estadistica etiqueta="Aceptadas" valor={justificadas} tono="exito" />
      </div>

      <Tarjeta>
        <div className="filtros">
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="filtro-estado-justificacion">
              Estado
            </label>
            <select
              id="filtro-estado-justificacion"
              className="entrada"
              value={estado}
              onChange={(evento) => setEstado(evento.target.value as EstadoJustificacion | '')}
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
          <Vacio titulo="Cargando justificaciones…" />
        ) : justificaciones.length === 0 ? (
          <Vacio
            titulo="No hay justificaciones"
            descripcion="Todavía no se han presentado solicitudes de justificación."
          />
        ) : (
          <ul className="lista-avisos">
            {justificaciones.map((justificacion) => (
              <li key={justificacion.id_justificacion} className="lista-avisos__item">
                <div className="lista-avisos__encabezado">
                  <Insignia tono={descripcionEstado(justificacion.estado).tono}>
                    {descripcionEstado(justificacion.estado).etiqueta}
                  </Insignia>
                  <span className="lista-avisos__fecha">
                    {formatearFechaHora(justificacion.solicitada_en)}
                  </span>
                </div>
                <p className="lista-avisos__titulo">
                  Estudiante {justificacion.id_estudiante} ·{' '}
                  {formatearFecha(justificacion.fecha_inicio)}
                  {justificacion.fecha_fin !== justificacion.fecha_inicio
                    ? ` al ${formatearFecha(justificacion.fecha_fin)}`
                    : ''}
                </p>
                <p className="lista-avisos__contenido">{justificacion.motivo}</p>
                {justificacion.documento_referencia ? (
                  <p className="lista-avisos__pie">Respaldo: {justificacion.documento_referencia}</p>
                ) : null}
                {justificacion.comentario_revision ? (
                  <p className="lista-avisos__pie">Respuesta: {justificacion.comentario_revision}</p>
                ) : null}

                {esDirector && justificacion.estado === 'pendiente' ? (
                  <div className="lista-avisos__acciones">
                    <button
                      type="button"
                      className="boton boton--primario boton--pequeno"
                      disabled={procesando}
                      onClick={() =>
                        void decidir(justificacion.id_justificacion, 'justificada', 'Justificación aceptada.')
                      }
                    >
                      Aceptar
                    </button>
                    <button
                      type="button"
                      className="boton boton--secundario boton--pequeno"
                      disabled={procesando}
                      onClick={() =>
                        void decidir(
                          justificacion.id_justificacion,
                          'requiere_informacion',
                          'Se solicita información adicional.'
                        )
                      }
                    >
                      Pedir información
                    </button>
                    <button
                      type="button"
                      className="boton boton--fantasma boton--pequeno"
                      disabled={procesando}
                      onClick={() =>
                        void decidir(
                          justificacion.id_justificacion,
                          'no_justificada',
                          'No se presentó respaldo suficiente.'
                        )
                      }
                    >
                      Rechazar
                    </button>
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </Tarjeta>

      {formularioAbierto ? (
        <FormularioJustificacion
          alCerrar={() => setFormularioAbierto(false)}
          alGuardar={() => {
            setFormularioAbierto(false);
            recargar();
          }}
          solicitar={solicitar}
        />
      ) : null}
    </div>
  );
}

interface PropiedadesFormulario {
  alCerrar: () => void;
  alGuardar: () => void;
  solicitar: (datos: NuevaJustificacion) => Promise<Justificacion>;
}

function FormularioJustificacion({ alCerrar, alGuardar, solicitar }: PropiedadesFormulario) {
  const [idEstudiante, setIdEstudiante] = useState('1');
  const [fechaInicio, setFechaInicio] = useState(() => new Date().toISOString().slice(0, 10));
  const [fechaFin, setFechaFin] = useState(() => new Date().toISOString().slice(0, 10));
  const [motivo, setMotivo] = useState('');
  const [documento, setDocumento] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const guardar = async (evento: FormEvent<HTMLFormElement>): Promise<void> => {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      const datos: NuevaJustificacion = {
        id_estudiante: Number(idEstudiante),
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
        motivo: motivo.trim(),
      };
      if (documento.trim()) {
        datos.documento_referencia = documento.trim();
      }
      await solicitar(datos);
      alGuardar();
    } catch (fallo) {
      setError(obtenerDetalleError(fallo).mensaje);
    } finally {
      setEnviando(false);
    }
  };

  return (
    <Ventana
      abierto
      titulo="Nueva justificación"
      descripcion="Indique el estudiante, el período de la ausencia y el motivo."
      onCerrar={alCerrar}
      pie={
        <>
          <button type="button" className="boton boton--secundario" onClick={alCerrar}>
            Cancelar
          </button>
          <button type="submit" form="formulario-justificacion" className="boton boton--primario" disabled={enviando}>
            {enviando ? 'Enviando…' : 'Enviar solicitud'}
          </button>
        </>
      }
    >
      <form id="formulario-justificacion" className="formulario" onSubmit={guardar}>
        {error ? (
          <AvisoVisual tono="peligro" titulo="No se pudo enviar la justificación">
            {error}
          </AvisoVisual>
        ) : null}

        <div className="campo">
          <label className="campo__etiqueta" htmlFor="justificacion-estudiante">
            Estudiante
          </label>
          <input
            id="justificacion-estudiante"
            className="entrada"
            type="number"
            min={1}
            value={idEstudiante}
            onChange={(evento) => setIdEstudiante(evento.target.value)}
            required
          />
        </div>

        <div className="rejilla rejilla--2">
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="justificacion-inicio">
              Fecha de inicio
            </label>
            <input
              id="justificacion-inicio"
              className="entrada"
              type="date"
              value={fechaInicio}
              onChange={(evento) => setFechaInicio(evento.target.value)}
              required
            />
          </div>
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="justificacion-fin">
              Fecha de fin
            </label>
            <input
              id="justificacion-fin"
              className="entrada"
              type="date"
              value={fechaFin}
              onChange={(evento) => setFechaFin(evento.target.value)}
              required
            />
          </div>
        </div>

        <div className="campo">
          <label className="campo__etiqueta" htmlFor="justificacion-motivo">
            Motivo
          </label>
          <textarea
            id="justificacion-motivo"
            className="entrada entrada--area"
            rows={4}
            value={motivo}
            onChange={(evento) => setMotivo(evento.target.value)}
            required
          />
        </div>

        <div className="campo">
          <label className="campo__etiqueta" htmlFor="justificacion-documento">
            Documento de respaldo (opcional)
          </label>
          <input
            id="justificacion-documento"
            className="entrada"
            type="text"
            value={documento}
            onChange={(evento) => setDocumento(evento.target.value)}
          />
        </div>
      </form>
    </Ventana>
  );
}

export default JustificationsPage;
