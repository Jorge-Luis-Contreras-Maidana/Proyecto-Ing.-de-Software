import { useState, type FormEvent } from 'react';
import { CircleCheck, Link2, Plus, UserRound, X } from 'lucide-react';
import { useAuth } from '../../auth/hooks/useAuth';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { formatearFecha, formatearFechaHora } from '../../../shared/lib/formatDate';
import { descripcionEstado } from '../../../shared/lib/etiquetas';
import { Aviso, Cargando, Insignia, Tarjeta, Vacio } from '../../../shared/ui';
import { confirmarTutor, registrarObservacion, vincularTutor } from '../api/studentsApi';
import { useEstudiante } from '../hooks/useStudents';
import type { TipoObservacion } from '../types/students.types';

const TIPOS_OBSERVACION: { valor: TipoObservacion; etiqueta: string }[] = [
  { valor: 'academica', etiqueta: 'Académica' },
  { valor: 'asistencia', etiqueta: 'Asistencia' },
  { valor: 'comportamiento', etiqueta: 'Comportamiento' },
  { valor: 'convivencia', etiqueta: 'Convivencia' },
  { valor: 'otra', etiqueta: 'Otra' },
];

export interface PropiedadesDetalleEstudiante {
  idEstudiante: number | null;
  alCerrar: () => void;
}

/** Ficha del estudiante: datos, observaciones y tutores vinculados. */
export function DetalleEstudiante({ idEstudiante, alCerrar }: PropiedadesDetalleEstudiante) {
  const { tieneRol } = useAuth();
  const { estudiante, observaciones, cargando, error, recargar } = useEstudiante(idEstudiante);

  const [tipoObservacion, setTipoObservacion] = useState<TipoObservacion>('academica');
  const [descripcion, setDescripcion] = useState('');
  const [confidencial, setConfidencial] = useState(false);
  const [enviandoObservacion, setEnviandoObservacion] = useState(false);

  const [idTutor, setIdTutor] = useState('');
  const [parentesco, setParentesco] = useState('Tutor legal');
  const [contactoPrincipal, setContactoPrincipal] = useState(false);
  const [enviandoVinculo, setEnviandoVinculo] = useState(false);

  const [mensaje, setMensaje] = useState<{ tono: 'exito' | 'peligro'; texto: string } | null>(null);

  const puedeObservar = tieneRol('director', 'profesor');
  const puedeVincular = tieneRol('director');

  const registrar = async (evento: FormEvent<HTMLFormElement>): Promise<void> => {
    evento.preventDefault();
    if (idEstudiante === null) {
      return;
    }
    setEnviandoObservacion(true);
    setMensaje(null);
    try {
      await registrarObservacion(idEstudiante, {
        tipo: tipoObservacion,
        descripcion: descripcion.trim(),
        confidencial,
      });
      setDescripcion('');
      setConfidencial(false);
      setMensaje({ tono: 'exito', texto: 'Observación registrada.' });
      recargar();
    } catch (fallo) {
      setMensaje({ tono: 'peligro', texto: obtenerDetalleError(fallo).mensaje });
    } finally {
      setEnviandoObservacion(false);
    }
  };

  const vincular = async (evento: FormEvent<HTMLFormElement>): Promise<void> => {
    evento.preventDefault();
    if (idEstudiante === null) {
      return;
    }
    const numero = Number(idTutor);
    if (!Number.isFinite(numero) || numero <= 0) {
      setMensaje({ tono: 'peligro', texto: 'Indique el número de identificación del tutor.' });
      return;
    }
    setEnviandoVinculo(true);
    setMensaje(null);
    try {
      const respuesta = await vincularTutor(idEstudiante, {
        id_tutor: numero,
        parentesco: parentesco.trim(),
        es_contacto_principal: contactoPrincipal,
      });
      setIdTutor('');
      setMensaje({ tono: 'exito', texto: respuesta.mensaje });
      recargar();
    } catch (fallo) {
      setMensaje({ tono: 'peligro', texto: obtenerDetalleError(fallo).mensaje });
    } finally {
      setEnviandoVinculo(false);
    }
  };

  const confirmar = async (id: number): Promise<void> => {
    if (idEstudiante === null) {
      return;
    }
    setMensaje(null);
    try {
      const respuesta = await confirmarTutor(idEstudiante, id);
      setMensaje({ tono: 'exito', texto: respuesta.mensaje });
      recargar();
    } catch (fallo) {
      setMensaje({ tono: 'peligro', texto: obtenerDetalleError(fallo).mensaje });
    }
  };

  if (idEstudiante === null) {
    return null;
  }

  return (
    <aside className="ficha">
      <header className="ficha__cabecera">
        <h2 className="ficha__titulo">Ficha del estudiante</h2>
        <button type="button" className="boton boton--icono" onClick={alCerrar} aria-label="Cerrar ficha">
          <X size={18} aria-hidden="true" />
        </button>
      </header>

      {cargando ? <Cargando texto="Cargando la ficha…" /> : null}

      {error ? (
        <Aviso tono="peligro" titulo="No se pudo cargar la ficha">
          {error}
        </Aviso>
      ) : null}

      {estudiante ? (
        <div className="ficha__contenido">
          <div className="ficha__datos">
            <p className="ficha__nombre">
              {estudiante.nombres} {estudiante.apellidos}
            </p>
            <p className="ficha__codigo">{estudiante.codigo_estudiante}</p>
            <dl className="lista-datos">
              <div className="lista-datos__item">
                <dt>Curso</dt>
                <dd>
                  {estudiante.curso
                    ? `${estudiante.curso.nivel} ${estudiante.curso.grado}${estudiante.curso.paralelo}`
                    : 'Sin curso'}
                </dd>
              </div>
              <div className="lista-datos__item">
                <dt>Turno</dt>
                <dd>{estudiante.curso?.turno ?? '—'}</dd>
              </div>
              <div className="lista-datos__item">
                <dt>Fecha de nacimiento</dt>
                <dd>{formatearFecha(estudiante.fecha_nacimiento)}</dd>
              </div>
              <div className="lista-datos__item">
                <dt>Estado</dt>
                <dd>
                  <Insignia tono={descripcionEstado(estudiante.estado).tono}>
                    {descripcionEstado(estudiante.estado).etiqueta}
                  </Insignia>
                </dd>
              </div>
            </dl>
          </div>

          {mensaje ? (
            <Aviso tono={mensaje.tono === 'exito' ? 'exito' : 'peligro'}>{mensaje.texto}</Aviso>
          ) : null}

          <Tarjeta titulo="Observaciones" descripcion={`${observaciones.length} registrada(s)`}>
            {observaciones.length === 0 ? (
              <Vacio titulo="Sin observaciones" descripcion="Todavía no hay observaciones registradas." />
            ) : (
              <ul className="lista-registros">
                {observaciones.map((observacion) => (
                  <li key={observacion.id_observacion} className="lista-registros__item">
                    <div className="lista-registros__encabezado">
                      <Insignia tono={descripcionEstado(observacion.tipo).tono}>
                        {descripcionEstado(observacion.tipo).etiqueta}
                      </Insignia>
                      <span className="lista-registros__fecha">
                        {formatearFechaHora(observacion.fecha_hora)}
                      </span>
                    </div>
                    <p className="lista-registros__texto">{observacion.descripcion}</p>
                    {observacion.confidencial ? (
                      <span className="lista-registros__nota">Registro confidencial</span>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}

            {puedeObservar ? (
              <form className="formulario formulario--compacto" onSubmit={registrar}>
                <div className="campo">
                  <label className="campo__etiqueta" htmlFor="tipo-observacion">
                    Tipo de observación
                  </label>
                  <select
                    id="tipo-observacion"
                    className="entrada"
                    value={tipoObservacion}
                    onChange={(evento) => setTipoObservacion(evento.target.value as TipoObservacion)}
                  >
                    {TIPOS_OBSERVACION.map((tipo) => (
                      <option key={tipo.valor} value={tipo.valor}>
                        {tipo.etiqueta}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="campo">
                  <label className="campo__etiqueta" htmlFor="descripcion-observacion">
                    Descripción
                  </label>
                  <textarea
                    id="descripcion-observacion"
                    className="entrada entrada--area"
                    rows={3}
                    value={descripcion}
                    onChange={(evento) => setDescripcion(evento.target.value)}
                    required
                    maxLength={2000}
                  />
                </div>
                <label className="campo__casilla">
                  <input
                    type="checkbox"
                    checked={confidencial}
                    onChange={(evento) => setConfidencial(evento.target.checked)}
                  />
                  Marcar como confidencial
                </label>
                <button type="submit" className="boton boton--primario" disabled={enviandoObservacion}>
                  <Plus size={16} aria-hidden="true" />
                  {enviandoObservacion ? 'Guardando…' : 'Registrar observación'}
                </button>
              </form>
            ) : null}
          </Tarjeta>

          <Tarjeta titulo="Tutores vinculados" descripcion={`${estudiante.tutores.length} vinculado(s)`}>
            {estudiante.tutores.length === 0 ? (
              <Vacio titulo="Sin tutores" descripcion="El estudiante no tiene tutores vinculados." />
            ) : (
              <ul className="lista-registros">
                {estudiante.tutores.map((tutor) => (
                  <li key={tutor.id_tutor} className="lista-registros__item">
                    <div className="lista-registros__encabezado">
                      <span className="lista-registros__titulo">
                        <UserRound size={16} aria-hidden="true" /> {tutor.nombre}
                      </span>
                      <Insignia tono={tutor.confirmado ? 'exito' : 'alerta'}>
                        {tutor.confirmado ? 'Confirmado' : 'Sin confirmar'}
                      </Insignia>
                    </div>
                    <p className="lista-registros__texto">
                      {tutor.parentesco}
                      {tutor.es_contacto_principal ? ' · Contacto principal' : ''}
                    </p>
                    {puedeVincular && !tutor.confirmado ? (
                      <button
                        type="button"
                        className="boton boton--secundario boton--pequeno"
                        onClick={() => void confirmar(tutor.id_tutor)}
                      >
                        <CircleCheck size={16} aria-hidden="true" /> Confirmar vínculo
                      </button>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}

            {puedeVincular ? (
              <form className="formulario formulario--compacto" onSubmit={vincular}>
                <div className="rejilla rejilla--2">
                  <div className="campo">
                    <label className="campo__etiqueta" htmlFor="id-tutor">
                      N.º del tutor
                    </label>
                    <input
                      id="id-tutor"
                      className="entrada"
                      type="number"
                      min={1}
                      value={idTutor}
                      onChange={(evento) => setIdTutor(evento.target.value)}
                      required
                    />
                  </div>
                  <div className="campo">
                    <label className="campo__etiqueta" htmlFor="parentesco">
                      Parentesco
                    </label>
                    <input
                      id="parentesco"
                      className="entrada"
                      type="text"
                      maxLength={30}
                      value={parentesco}
                      onChange={(evento) => setParentesco(evento.target.value)}
                      required
                    />
                  </div>
                </div>
                <label className="campo__casilla">
                  <input
                    type="checkbox"
                    checked={contactoPrincipal}
                    onChange={(evento) => setContactoPrincipal(evento.target.checked)}
                  />
                  Contacto principal
                </label>
                <button type="submit" className="boton boton--primario" disabled={enviandoVinculo}>
                  <Link2 size={16} aria-hidden="true" />
                  {enviandoVinculo ? 'Vinculando…' : 'Vincular tutor'}
                </button>
              </form>
            ) : null}
          </Tarjeta>
        </div>
      ) : null}
    </aside>
  );
}
