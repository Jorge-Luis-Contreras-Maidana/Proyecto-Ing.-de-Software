import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { Megaphone, Plus, Send } from 'lucide-react';
import { useAuth } from '../../auth/hooks/useAuth';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { descripcionEstado } from '../../../shared/lib/etiquetas';
import { formatearFechaHora } from '../../../shared/lib/formatDate';
import { Aviso as AvisoVisual, Encabezado, Estadistica, Insignia, Tarjeta, Vacio, Ventana } from '../../../shared/ui';
import { crearAviso } from '../api/announcementsApi';
import { useAvisos } from '../hooks/useAnnouncements';
import type { EstadoAviso } from '../types/announcements.types';

const ESTADOS: { valor: EstadoAviso | ''; etiqueta: string }[] = [
  { valor: '', etiqueta: 'Todos' },
  { valor: 'publicado', etiqueta: 'Publicados' },
  { valor: 'borrador', etiqueta: 'Borradores' },
  { valor: 'archivado', etiqueta: 'Archivados' },
];

const ROLES = ['director', 'profesor', 'tutor', 'estudiante'];

/** Avisos institucionales de la unidad educativa. */
export function AnnouncementsPage() {
  const { tieneRol } = useAuth();
  const esDirector = tieneRol('director');

  const [estado, setEstado] = useState<EstadoAviso | ''>('');
  const [soloNoLeidos, setSoloNoLeidos] = useState(false);
  const { avisos, total, cargando, error, recargar, marcarLeido, publicar, procesando } = useAvisos({
    estado: estado === '' ? null : estado,
    solo_no_leidos: soloNoLeidos,
  });

  const [formularioAbierto, setFormularioAbierto] = useState(false);
  const [mensaje, setMensaje] = useState<{ tono: 'exito' | 'peligro'; texto: string } | null>(null);

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

  const publicados = avisos.filter((aviso) => aviso.estado === 'publicado').length;
  const noLeidos = avisos.filter((aviso) => !aviso.leido).length;

  return (
    <div className="pagina">
      <Encabezado
        titulo="Avisos"
        descripcion="Comunicados internos de la unidad educativa y avisos dirigidos a familias."
        icono={<Megaphone size={22} aria-hidden="true" />}
        acciones={
          esDirector ? (
            <button type="button" className="boton boton--primario" onClick={() => setFormularioAbierto(true)}>
              <Plus size={16} aria-hidden="true" /> Nuevo aviso
            </button>
          ) : null
        }
      />

      {mensaje ? (
        <AvisoVisual tono={mensaje.tono === 'exito' ? 'exito' : 'peligro'}>{mensaje.texto}</AvisoVisual>
      ) : null}

      {error ? (
        <AvisoVisual tono="peligro" titulo="No se pudieron cargar los avisos">
          {error}
        </AvisoVisual>
      ) : null}

      <div className="rejilla rejilla--3">
        <Estadistica etiqueta="Avisos" valor={total} icono={<Megaphone size={18} aria-hidden="true" />} />
        <Estadistica etiqueta="Publicados" valor={publicados} tono="exito" />
        <Estadistica etiqueta="Sin leer" valor={noLeidos} tono="alerta" />
      </div>

      <Tarjeta>
        <div className="filtros">
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="filtro-estado-aviso">
              Estado
            </label>
            <select
              id="filtro-estado-aviso"
              className="entrada"
              value={estado}
              onChange={(evento) => setEstado(evento.target.value as EstadoAviso | '')}
            >
              {ESTADOS.map((opcion) => (
                <option key={opcion.valor} value={opcion.valor}>
                  {opcion.etiqueta}
                </option>
              ))}
            </select>
          </div>
          <label className="campo__casilla">
            <input
              type="checkbox"
              checked={soloNoLeidos}
              onChange={(evento) => setSoloNoLeidos(evento.target.checked)}
            />
            Mostrar solo los no leídos
          </label>
        </div>

        {cargando ? (
          <Vacio titulo="Cargando avisos…" />
        ) : avisos.length === 0 ? (
          <Vacio titulo="No hay avisos" descripcion="Todavía no hay avisos publicados." />
        ) : (
          <ul className="lista-avisos">
            {avisos.map((aviso) => (
              <li key={aviso.id_aviso} className={`lista-avisos__item ${aviso.leido ? '' : 'lista-avisos__item--nuevo'}`}>
                <div className="lista-avisos__encabezado">
                  <Insignia tono={descripcionEstado(aviso.estado).tono}>
                    {descripcionEstado(aviso.estado).etiqueta}
                  </Insignia>
                  {aviso.importante ? <Insignia tono="peligro">Importante</Insignia> : null}
                  <span className="lista-avisos__fecha">
                    {aviso.publicado_en ? formatearFechaHora(aviso.publicado_en) : 'Sin publicar'}
                  </span>
                </div>
                <p className="lista-avisos__titulo">{aviso.titulo}</p>
                <p className="lista-avisos__contenido">{aviso.contenido}</p>
                <p className="lista-avisos__pie">
                  Lectores: {aviso.total_lectores}
                  {aviso.roles_destinatarios.length > 0
                    ? ` · Destinatarios: ${aviso.roles_destinatarios.join(', ')}`
                    : ' · Destinatarios: todos'}
                </p>
                <div className="lista-avisos__acciones">
                  {!aviso.leido ? (
                    <button
                      type="button"
                      className="boton boton--fantasma boton--pequeno"
                      disabled={procesando}
                      onClick={() => void ejecutar(() => marcarLeido(aviso.id_aviso), 'Aviso marcado como leído.')}
                    >
                      Marcar como leído
                    </button>
                  ) : null}
                  {esDirector && aviso.estado === 'borrador' ? (
                    <button
                      type="button"
                      className="boton boton--primario boton--pequeno"
                      disabled={procesando}
                      onClick={() => void ejecutar(() => publicar(aviso.id_aviso), 'Aviso publicado.')}
                    >
                      <Send size={14} aria-hidden="true" /> Publicar
                    </button>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>
        )}
      </Tarjeta>

      {tieneRol('director', 'profesor') ? (
        <Tarjeta titulo="Avisos de inasistencia docente">
          <p className="texto-suave">
            Revise los avisos generados cuando un docente no impartió su clase.
          </p>
          <Link className="boton boton--secundario" to="/avisos-inasistencia-docente">
            Ver avisos de inasistencia docente
          </Link>
        </Tarjeta>
      ) : null}

      {formularioAbierto ? (
        <FormularioAviso
          alCerrar={() => setFormularioAbierto(false)}
          alGuardar={() => {
            setFormularioAbierto(false);
            recargar();
          }}
        />
      ) : null}
    </div>
  );
}

interface PropiedadesFormularioAviso {
  alCerrar: () => void;
  alGuardar: () => void;
}

function FormularioAviso({ alCerrar, alGuardar }: PropiedadesFormularioAviso) {
  const [titulo, setTitulo] = useState('');
  const [contenido, setContenido] = useState('');
  const [importante, setImportante] = useState(false);
  const [roles, setRoles] = useState<string[]>([]);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const alternarRol = (rol: string): void => {
    setRoles((actuales) =>
      actuales.includes(rol) ? actuales.filter((item) => item !== rol) : [...actuales, rol]
    );
  };

  const guardar = async (evento: FormEvent<HTMLFormElement>): Promise<void> => {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      await crearAviso({
        titulo: titulo.trim(),
        contenido: contenido.trim(),
        importante,
        roles_destinatarios: roles.length > 0 ? roles : undefined,
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
      titulo="Nuevo aviso"
      descripcion="El aviso se crea como borrador y luego puede publicarse."
      onCerrar={alCerrar}
      pie={
        <>
          <button type="button" className="boton boton--secundario" onClick={alCerrar}>
            Cancelar
          </button>
          <button type="submit" form="formulario-aviso" className="boton boton--primario" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Guardar borrador'}
          </button>
        </>
      }
    >
      <form id="formulario-aviso" className="formulario" onSubmit={guardar}>
        {error ? (
          <AvisoVisual tono="peligro" titulo="No se pudo crear el aviso">
            {error}
          </AvisoVisual>
        ) : null}

        <div className="campo">
          <label className="campo__etiqueta" htmlFor="titulo-aviso">
            Título
          </label>
          <input
            id="titulo-aviso"
            className="entrada"
            type="text"
            maxLength={200}
            value={titulo}
            onChange={(evento) => setTitulo(evento.target.value)}
            required
          />
        </div>

        <div className="campo">
          <label className="campo__etiqueta" htmlFor="contenido-aviso">
            Contenido
          </label>
          <textarea
            id="contenido-aviso"
            className="entrada entrada--area"
            rows={6}
            value={contenido}
            onChange={(evento) => setContenido(evento.target.value)}
            required
          />
        </div>

        <label className="campo__casilla">
          <input
            type="checkbox"
            checked={importante}
            onChange={(evento) => setImportante(evento.target.checked)}
          />
          Marcar como importante
        </label>

        <fieldset className="campo campo--grupo">
          <legend className="campo__etiqueta">Roles destinatarios</legend>
          <p className="formulario__ayuda">Si no elige ninguno, el aviso se envía a todos.</p>
          {ROLES.map((rol) => (
            <label key={rol} className="campo__casilla">
              <input type="checkbox" checked={roles.includes(rol)} onChange={() => alternarRol(rol)} />
              {rol}
            </label>
          ))}
        </fieldset>
      </form>
    </Ventana>
  );
}

export default AnnouncementsPage;
