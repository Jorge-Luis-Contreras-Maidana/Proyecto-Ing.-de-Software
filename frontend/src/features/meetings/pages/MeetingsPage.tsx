import { useState, type FormEvent } from 'react';
import { CalendarPlus, GraduationCap } from 'lucide-react';
import { useAuth } from '../../auth/hooks/useAuth';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { descripcionEstado } from '../../../shared/lib/etiquetas';
import { formatearFechaHora, aCampoFechaHoraLocal } from '../../../shared/lib/formatDate';
import { Aviso as AvisoVisual, Encabezado, Estadistica, Insignia, Tarjeta, Vacio, Ventana } from '../../../shared/ui';
import { useCitas } from '../hooks/useMeetings';
import type { EstadoCita, NuevaCita, Cita } from '../types/meetings.types';

const ESTADOS: { valor: EstadoCita | ''; etiqueta: string }[] = [
  { valor: '', etiqueta: 'Todas' },
  { valor: 'programada', etiqueta: 'Programadas' },
  { valor: 'confirmada', etiqueta: 'Confirmadas' },
  { valor: 'realizada', etiqueta: 'Realizadas' },
  { valor: 'cancelada', etiqueta: 'Canceladas' },
  { valor: 'reprogramada', etiqueta: 'Reprogramadas' },
];

/** Citas de seguimiento con los tutores de los estudiantes. */
export function MeetingsPage() {
  const { tieneRol } = useAuth();
  const [estado, setEstado] = useState<EstadoCita | ''>('');
  const { citas, total, cargando, error, recargar, cambiarEstado, convocar, procesando } = useCitas({
    estado: estado === '' ? null : estado,
  });
  const [formularioAbierto, setFormularioAbierto] = useState(false);
  const [mensaje, setMensaje] = useState<{ tono: 'exito' | 'peligro'; texto: string } | null>(null);

  const programadas = citas.filter((cita) => cita.estado === 'programada').length;
  const realizadas = citas.filter((cita) => cita.estado === 'realizada').length;

  const ejecutar = async (accion: () => Promise<void>, texto: string): Promise<void> => {
    setMensaje(null);
    try {
      await accion();
      setMensaje({ tono: 'exito', texto });
      recargar();
    } catch (fallo) {
      setMensaje({ tono: 'peligro', texto: obtenerDetalleError(fallo).mensaje });
    }
  };

  return (
    <div className="pagina">
      <Encabezado
        titulo="Citas de seguimiento"
        descripcion="Reuniones entre el personal docente y los tutores para revisar los casos de los estudiantes."
        icono={<GraduationCap size={22} aria-hidden="true" />}
        acciones={
          tieneRol('director', 'profesor') ? (
            <button type="button" className="boton boton--primario" onClick={() => setFormularioAbierto(true)}>
              <CalendarPlus size={16} aria-hidden="true" /> Convocar cita
            </button>
          ) : null
        }
      />

      {mensaje ? (
        <AvisoVisual tono={mensaje.tono === 'exito' ? 'exito' : 'peligro'}>{mensaje.texto}</AvisoVisual>
      ) : null}

      {error ? (
        <AvisoVisual tono="peligro" titulo="No se pudieron cargar las citas">
          {error}
        </AvisoVisual>
      ) : null}

      <div className="rejilla rejilla--3">
        <Estadistica etiqueta="Citas" valor={total} icono={<GraduationCap size={18} aria-hidden="true" />} />
        <Estadistica etiqueta="Programadas" valor={programadas} tono="info" />
        <Estadistica etiqueta="Realizadas" valor={realizadas} tono="exito" />
      </div>

      <Tarjeta>
        <div className="filtros">
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="filtro-estado-cita">
              Estado
            </label>
            <select
              id="filtro-estado-cita"
              className="entrada"
              value={estado}
              onChange={(evento) => setEstado(evento.target.value as EstadoCita | '')}
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
          <Vacio titulo="Cargando citas…" />
        ) : citas.length === 0 ? (
          <Vacio titulo="No hay citas" descripcion="Todavía no hay citas registradas." />
        ) : (
          <ul className="lista-avisos">
            {citas.map((cita) => (
              <li key={cita.id_citacion} className="lista-avisos__item">
                <div className="lista-avisos__encabezado">
                  <Insignia tono={descripcionEstado(cita.estado).tono}>
                    {descripcionEstado(cita.estado).etiqueta}
                  </Insignia>
                  <span className="lista-avisos__fecha">{formatearFechaHora(cita.fecha_hora)}</span>
                </div>
                <p className="lista-avisos__titulo">Estudiante {cita.id_estudiante}</p>
                <p className="lista-avisos__contenido">{cita.motivo}</p>
                <p className="lista-avisos__pie">
                  Tutor {cita.id_tutor} · Profesor {cita.id_profesor}
                  {cita.observaciones ? ` · ${cita.observaciones}` : ''}
                </p>
                {cita.estado === 'programada' ? (
                  <div className="lista-avisos__acciones">
                    <button
                      type="button"
                      className="boton boton--secundario boton--pequeno"
                      disabled={procesando}
                      onClick={() =>
                        void ejecutar(
                          () => cambiarEstado(cita.id_citacion, { estado: 'confirmada' }),
                          'Cita confirmada.'
                        )
                      }
                    >
                      Confirmar
                    </button>
                    <button
                      type="button"
                      className="boton boton--fantasma boton--pequeno"
                      disabled={procesando}
                      onClick={() =>
                        void ejecutar(
                          () => cambiarEstado(cita.id_citacion, { estado: 'cancelada' }),
                          'Cita cancelada.'
                        )
                      }
                    >
                      Cancelar
                    </button>
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </Tarjeta>

      {formularioAbierto ? (
        <FormularioCita
          alCerrar={() => setFormularioAbierto(false)}
          alGuardar={() => {
            setFormularioAbierto(false);
            recargar();
          }}
          convocar={convocar}
        />
      ) : null}
    </div>
  );
}

interface PropiedadesFormularioCita {
  alCerrar: () => void;
  alGuardar: () => void;
  convocar: (datos: NuevaCita) => Promise<Cita>;
}

function FormularioCita({ alCerrar, alGuardar, convocar }: PropiedadesFormularioCita) {
  const [idEstudiante, setIdEstudiante] = useState('1');
  const [idTutor, setIdTutor] = useState('1');
  const [idProfesor, setIdProfesor] = useState('1');
  const [fechaHora, setFechaHora] = useState(() => aCampoFechaHoraLocal(new Date().toISOString()));
  const [motivo, setMotivo] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const guardar = async (evento: FormEvent<HTMLFormElement>): Promise<void> => {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      await convocar({
        id_estudiante: Number(idEstudiante),
        id_tutor: Number(idTutor),
        id_profesor: Number(idProfesor),
        fecha_hora: new Date(fechaHora).toISOString(),
        motivo: motivo.trim(),
      });
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
      titulo="Convocar cita"
      descripcion="Indique el estudiante, el tutor y el motivo de la reunión."
      onCerrar={alCerrar}
      pie={
        <>
          <button type="button" className="boton boton--secundario" onClick={alCerrar}>
            Cancelar
          </button>
          <button type="submit" form="formulario-cita" className="boton boton--primario" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Convocar'}
          </button>
        </>
      }
    >
      <form id="formulario-cita" className="formulario" onSubmit={guardar}>
        {error ? (
          <AvisoVisual tono="peligro" titulo="No se pudo convocar la cita">
            {error}
          </AvisoVisual>
        ) : null}

        <div className="rejilla rejilla--3">
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="cita-estudiante">
              Estudiante
            </label>
            <input
              id="cita-estudiante"
              className="entrada"
              type="number"
              min={1}
              value={idEstudiante}
              onChange={(evento) => setIdEstudiante(evento.target.value)}
              required
            />
          </div>
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="cita-tutor">
              Tutor
            </label>
            <input
              id="cita-tutor"
              className="entrada"
              type="number"
              min={1}
              value={idTutor}
              onChange={(evento) => setIdTutor(evento.target.value)}
              required
            />
          </div>
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="cita-profesor">
              Profesor
            </label>
            <input
              id="cita-profesor"
              className="entrada"
              type="number"
              min={1}
              value={idProfesor}
              onChange={(evento) => setIdProfesor(evento.target.value)}
              required
            />
          </div>
        </div>

        <div className="campo">
          <label className="campo__etiqueta" htmlFor="cita-fecha">
            Fecha y hora
          </label>
          <input
            id="cita-fecha"
            className="entrada"
            type="datetime-local"
            value={fechaHora}
            onChange={(evento) => setFechaHora(evento.target.value)}
            required
          />
        </div>

        <div className="campo">
          <label className="campo__etiqueta" htmlFor="cita-motivo">
            Motivo
          </label>
          <textarea
            id="cita-motivo"
            className="entrada entrada--area"
            rows={4}
            value={motivo}
            onChange={(evento) => setMotivo(evento.target.value)}
            required
          />
        </div>
      </form>
    </Ventana>
  );
}

export default MeetingsPage;
