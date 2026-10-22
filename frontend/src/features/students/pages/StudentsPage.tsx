import { useMemo, useState, type FormEvent } from 'react';
import { GraduationCap, Pencil, Plus, Search, Trash2, Users } from 'lucide-react';
import { useAuth } from '../../auth/hooks/useAuth';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { normalizarTexto } from '../../../shared/lib/text';
import { descripcionEstado } from '../../../shared/lib/etiquetas';
import { useValorConRetraso } from '../../../shared/hooks/useValorConRetraso';
import { Aviso, Encabezado, Insignia, Paginacion, Tabla, Tarjeta, Ventana } from '../../../shared/ui';
import type { ColumnaTabla } from '../../../shared/ui';
import { DetalleEstudiante } from '../components/DetalleEstudiante';
import { crearEstudiante, actualizarEstudiante, retirarEstudiante } from '../api/studentsApi';
import { useCursosDisponibles, useEstudiantes } from '../hooks/useStudents';
import type { Estudiante, EstadoEstudiante } from '../types/students.types';

const ESTADOS: { valor: EstadoEstudiante | 'todos'; etiqueta: string }[] = [
  { valor: 'activo', etiqueta: 'Activos' },
  { valor: 'retirado', etiqueta: 'Retirados' },
  { valor: 'egresado', etiqueta: 'Egresados' },
  { valor: 'todos', etiqueta: 'Todos' },
];

const POR_PAGINA = 20;

/** Listado de estudiantes con búsqueda, filtros y ficha de detalle. */
export function StudentsPage() {
  const { tieneRol } = useAuth();
  const esDirector = tieneRol('director');
  const cursos = useCursosDisponibles();

  const [busqueda, setBusqueda] = useState('');
  const [idCurso, setIdCurso] = useState<number | ''>('');
  const [estado, setEstado] = useState<EstadoEstudiante | 'todos'>('activo');
  const [pagina, setPagina] = useState(1);

  const busquedaRetrasada = useValorConRetraso(busqueda);

  const filtros = useMemo(
    () => ({
      q: normalizarTexto(busquedaRetrasada),
      id_curso: idCurso === '' ? null : idCurso,
      estado,
      page: pagina,
      per_page: POR_PAGINA,
    }),
    [busquedaRetrasada, idCurso, estado, pagina]
  );

  const { estudiantes, total, cargando, error, recargar } = useEstudiantes(filtros);

  const [estudianteSeleccionado, setEstudianteSeleccionado] = useState<number | null>(null);
  const [formularioAbierto, setFormularioAbierto] = useState(false);
  const [estudianteEnEdicion, setEstudianteEnEdicion] = useState<Estudiante | null>(null);
  const [mensaje, setMensaje] = useState<{ tono: 'exito' | 'peligro'; texto: string } | null>(null);

  const totalPaginas = Math.max(1, Math.ceil(total / POR_PAGINA));

  const columnas: ColumnaTabla<Estudiante>[] = [
    {
      clave: 'codigo_estudiante',
      etiqueta: 'Código',
      render: (estudiante) => <span className="tabla__codigo">{estudiante.codigo_estudiante}</span>,
    },
    {
      clave: 'nombres',
      etiqueta: 'Estudiante',
      render: (estudiante) => (
        <span>
          <strong>
            {estudiante.nombres} {estudiante.apellidos}
          </strong>
        </span>
      ),
    },
    {
      clave: 'curso',
      etiqueta: 'Curso',
      render: (estudiante) =>
        estudiante.curso
          ? `${estudiante.curso.nivel} ${estudiante.curso.grado}${estudiante.curso.paralelo}`
          : '—',
    },
    { clave: 'turno', etiqueta: 'Turno', render: (estudiante) => estudiante.curso?.turno ?? '—' },
    {
      clave: 'estado',
      etiqueta: 'Estado',
      render: (estudiante) => (
        <Insignia tono={descripcionEstado(estudiante.estado).tono}>
          {descripcionEstado(estudiante.estado).etiqueta}
        </Insignia>
      ),
    },
    {
      clave: 'acciones',
      etiqueta: 'Acciones',
      alineacion: 'derecha',
      render: (estudiante) => (
        <div className="tabla__acciones">
          <button
            type="button"
            className="boton boton--secundario boton--pequeno"
            onClick={() => setEstudianteSeleccionado(estudiante.id_estudiante)}
          >
            Ver ficha
          </button>
          {esDirector ? (
            <>
              <button
                type="button"
                className="boton boton--fantasma boton--pequeno"
                onClick={() => {
                  setEstudianteEnEdicion(estudiante);
                  setFormularioAbierto(true);
                }}
              >
                <Pencil size={14} aria-hidden="true" /> Editar
              </button>
              <button
                type="button"
                className="boton boton--peligro boton--pequeno"
                onClick={() => void darDeBaja(estudiante)}
              >
                <Trash2 size={14} aria-hidden="true" /> Baja
              </button>
            </>
          ) : null}
        </div>
      ),
    },
  ];

  const darDeBaja = async (estudiante: Estudiante): Promise<void> => {
    const confirmado = window.confirm(
      `¿Dar de baja a ${estudiante.nombres} ${estudiante.apellidos}? Se conservará su historial.`
    );
    if (!confirmado) {
      return;
    }
    setMensaje(null);
    try {
      const respuesta = await retirarEstudiante(estudiante.id_estudiante);
      setMensaje({ tono: 'exito', texto: respuesta.mensaje });
      recargar();
    } catch (fallo) {
      setMensaje({ tono: 'peligro', texto: obtenerDetalleError(fallo).mensaje });
    }
  };

  const cambiarPagina = (nuevaPagina: number): void => {
    setPagina(nuevaPagina);
  };

  return (
    <div className="pagina">
      <Encabezado
        titulo="Estudiantes"
        descripcion="Consulte el padrón de estudiantes, sus observaciones y los tutores vinculados."
        icono={<Users size={22} aria-hidden="true" />}
        acciones={
          esDirector ? (
            <button
              type="button"
              className="boton boton--primario"
              onClick={() => {
                setEstudianteEnEdicion(null);
                setFormularioAbierto(true);
              }}
            >
              <Plus size={16} aria-hidden="true" /> Nuevo estudiante
            </button>
          ) : null
        }
      />

      {mensaje ? (
        <Aviso tono={mensaje.tono === 'exito' ? 'exito' : 'peligro'}>{mensaje.texto}</Aviso>
      ) : null}

      <Tarjeta>
        <div className="filtros">
          <div className="campo campo--buscador">
            <label className="campo__etiqueta" htmlFor="busqueda-estudiante">
              Buscar
            </label>
            <div className="campo__con-icono">
              <Search size={18} aria-hidden="true" />
              <input
                id="busqueda-estudiante"
                className="entrada"
                type="search"
                placeholder="Nombre, apellido o código"
                value={busqueda}
                onChange={(evento) => {
                  setBusqueda(evento.target.value);
                  setPagina(1);
                }}
              />
            </div>
          </div>

          <div className="campo">
            <label className="campo__etiqueta" htmlFor="filtro-curso">
              Curso
            </label>
            <select
              id="filtro-curso"
              className="entrada"
              value={idCurso}
              onChange={(evento) => {
                setIdCurso(evento.target.value === '' ? '' : Number(evento.target.value));
                setPagina(1);
              }}
            >
              <option value="">Todos los cursos</option>
              {cursos.map((curso) => (
                <option key={curso.id_curso} value={curso.id_curso}>
                  {curso.nivel} {curso.grado}
                  {curso.paralelo}
                </option>
              ))}
            </select>
          </div>

          <div className="campo">
            <label className="campo__etiqueta" htmlFor="filtro-estado">
              Estado
            </label>
            <select
              id="filtro-estado"
              className="entrada"
              value={estado}
              onChange={(evento) => {
                setEstado(evento.target.value as EstadoEstudiante | 'todos');
                setPagina(1);
              }}
            >
              {ESTADOS.map((opcion) => (
                <option key={opcion.valor} value={opcion.valor}>
                  {opcion.etiqueta}
                </option>
              ))}
            </select>
          </div>
        </div>

        {error ? (
          <Aviso tono="peligro" titulo="No se pudo cargar el listado">
            {error}
          </Aviso>
        ) : null}

        <Tabla
          columnas={columnas}
          filas={estudiantes}
          claveFila={(estudiante) => estudiante.id_estudiante}
          cargando={cargando}
          mensajeVacio="No hay estudiantes que coincidan con la búsqueda"
          descripcionVacio="Pruebe con otros filtros o registre un nuevo estudiante."
        />

        <Paginacion
          pagina={pagina}
          totalPaginas={totalPaginas}
          total={total}
          onCambioPagina={cambiarPagina}
        />
      </Tarjeta>

      {estudianteSeleccionado !== null ? (
        <DetalleEstudiante
          idEstudiante={estudianteSeleccionado}
          alCerrar={() => setEstudianteSeleccionado(null)}
        />
      ) : null}

      {formularioAbierto ? (
        <FormularioEstudiante
          key={estudianteEnEdicion?.id_estudiante ?? 'nuevo'}
          abierto={formularioAbierto}
          estudiante={estudianteEnEdicion}
          cursos={cursos}
          alCerrar={() => setFormularioAbierto(false)}
          alGuardar={() => {
            setFormularioAbierto(false);
            setEstudianteEnEdicion(null);
            recargar();
          }}
        />
      ) : null}
    </div>
  );
}

interface PropiedadesFormulario {
  abierto: boolean;
  estudiante: Estudiante | null;
  cursos: { id_curso: number; nivel: string; grado: number; paralelo: string }[];
  alCerrar: () => void;
  alGuardar: () => void;
}

function FormularioEstudiante({
  abierto,
  estudiante,
  cursos,
  alCerrar,
  alGuardar,
}: PropiedadesFormulario) {
  const [codigo, setCodigo] = useState(estudiante?.codigo_estudiante ?? '');
  const [nombres, setNombres] = useState(estudiante?.nombres ?? '');
  const [apellidos, setApellidos] = useState(estudiante?.apellidos ?? '');
  const [fechaNacimiento, setFechaNacimiento] = useState(estudiante?.fecha_nacimiento ?? '');
  const [genero, setGenero] = useState(estudiante?.genero ?? '');
  const [idCurso, setIdCurso] = useState(estudiante?.curso ? String(estudiante.curso.id_curso) : '');
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const guardar = async (evento: FormEvent<HTMLFormElement>): Promise<void> => {
    evento.preventDefault();
    setEnviando(true);
    setError(null);

    try {
      if (estudiante) {
        await actualizarEstudiante(estudiante.id_estudiante, {
          nombres: nombres.trim(),
          apellidos: apellidos.trim(),
          fecha_nacimiento: fechaNacimiento,
          genero: genero.trim() ? genero.trim() : null,
          id_curso: idCurso ? Number(idCurso) : undefined,
        });
      } else {
        await crearEstudiante({
          codigo_estudiante: codigo.trim(),
          nombres: nombres.trim(),
          apellidos: apellidos.trim(),
          fecha_nacimiento: fechaNacimiento,
          genero: genero.trim() ? genero.trim() : null,
          id_curso: Number(idCurso),
        });
      }
      alGuardar();
    } catch (fallo) {
      setError(obtenerDetalleError(fallo).mensaje);
    } finally {
      setEnviando(false);
    }
  };

  return (
    <Ventana
      abierto={abierto}
      titulo={estudiante ? 'Editar estudiante' : 'Nuevo estudiante'}
      descripcion={
        estudiante
          ? 'Modifique los datos del estudiante y guarde los cambios.'
          : 'Registre un estudiante en la unidad educativa.'
      }
      onCerrar={alCerrar}
      pie={
        <>
          <button type="button" className="boton boton--secundario" onClick={alCerrar}>
            Cancelar
          </button>
          <button type="submit" form="formulario-estudiante" className="boton boton--primario" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Guardar'}
          </button>
        </>
      }
    >
      <form id="formulario-estudiante" className="formulario" onSubmit={guardar}>
        {error ? (
          <Aviso tono="peligro" titulo="No se pudo guardar">
            {error}
          </Aviso>
        ) : null}

        {!estudiante ? (
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="codigo-estudiante">
              Código de estudiante
            </label>
            <input
              id="codigo-estudiante"
              className="entrada"
              type="text"
              maxLength={25}
              value={codigo}
              onChange={(evento) => setCodigo(evento.target.value)}
              required
            />
          </div>
        ) : null}

        <div className="rejilla rejilla--2">
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="nombres-estudiante">
              Nombres
            </label>
            <input
              id="nombres-estudiante"
              className="entrada"
              type="text"
              maxLength={80}
              value={nombres}
              onChange={(evento) => setNombres(evento.target.value)}
              required
            />
          </div>
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="apellidos-estudiante">
              Apellidos
            </label>
            <input
              id="apellidos-estudiante"
              className="entrada"
              type="text"
              maxLength={100}
              value={apellidos}
              onChange={(evento) => setApellidos(evento.target.value)}
              required
            />
          </div>
        </div>

        <div className="rejilla rejilla--2">
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="fecha-nacimiento">
              Fecha de nacimiento
            </label>
            <input
              id="fecha-nacimiento"
              className="entrada"
              type="date"
              value={fechaNacimiento}
              onChange={(evento) => setFechaNacimiento(evento.target.value)}
              required
            />
          </div>
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="genero-estudiante">
              Género
            </label>
            <input
              id="genero-estudiante"
              className="entrada"
              type="text"
              maxLength={20}
              value={genero}
              onChange={(evento) => setGenero(evento.target.value)}
              placeholder="Femenino / Masculino / Otro"
            />
          </div>
        </div>

        <div className="campo">
          <label className="campo__etiqueta" htmlFor="curso-estudiante">
            Curso
          </label>
          <select
            id="curso-estudiante"
            className="entrada"
            value={idCurso}
            onChange={(evento) => setIdCurso(evento.target.value)}
            required
          >
            <option value="">Seleccione un curso</option>
            {cursos.map((curso) => (
              <option key={curso.id_curso} value={curso.id_curso}>
                {curso.nivel} {curso.grado}
                {curso.paralelo}
              </option>
            ))}
          </select>
        </div>

        <p className="formulario__ayuda">
          <GraduationCap size={15} aria-hidden="true" />
          El curso determina el horario y el padrón donde se registra la asistencia.
        </p>
      </form>
    </Ventana>
  );
}

export default StudentsPage;
