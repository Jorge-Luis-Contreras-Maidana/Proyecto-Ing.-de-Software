import { useMemo, useState, type FormEvent } from 'react';
import { CalendarDays, ClipboardCheck, History, Users } from 'lucide-react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { descripcionEstado } from '../../../shared/lib/etiquetas';
import { formatearFecha, formatearHora } from '../../../shared/lib/formatDate';
import { Aviso, Encabezado, Estadistica, Insignia, Tabla, Tarjeta, Vacio } from '../../../shared/ui';
import type { ColumnaTabla } from '../../../shared/ui';
import { marcarManual } from '../api/attendanceApi';
import { useDetalleSesion, useHistorial, useSesionesDeHoy } from '../hooks/useAttendance';
import type {
  EstadoAsistencia,
  EstudianteSesion,
  HistorialAsistencia,
  SesionClase,
} from '../types/attendance.types';

const ESTADOS_MANUALES: { valor: EstadoAsistencia; etiqueta: string }[] = [
  { valor: 'presente', etiqueta: 'Presente' },
  { valor: 'tarde', etiqueta: 'Tarde' },
  { valor: 'ausente', etiqueta: 'Ausente' },
  { valor: 'justificada', etiqueta: 'Justificada' },
  { valor: 'pendiente', etiqueta: 'Pendiente' },
];

/** Control de asistencia: sesiones del día, detalle y registro manual. */
export function AttendancePage() {
  const { sesiones, cargando, error, recargar } = useSesionesDeHoy();
  const [idSesion, setIdSesion] = useState<number | null>(null);

  const { sesion, cargando: cargandoDetalle, recargar: recargarDetalle } = useDetalleSesion(idSesion);

  const [idEstudianteHistorial, setIdEstudianteHistorial] = useState('');
  const [desde, setDesde] = useState('');
  const [hasta, setHasta] = useState('');
  const { historial, cargando: cargandoHistorial, error: errorHistorial } = useHistorial(
    idEstudianteHistorial ? Number(idEstudianteHistorial) : null,
    { desde, hasta }
  );

  const mensajeSesion = useMemo(() => {
    if (!sesion) {
      return null;
    }
    return `${sesion.curso} · ${sesion.hora_inicio_prevista} - ${sesion.hora_fin_prevista}`;
  }, [sesion]);

  const columnasEstudiantes: ColumnaTabla<EstudianteSesion>[] = [
    {
      clave: 'codigo_estudiante',
      etiqueta: 'Código',
      render: (estudiante) => <span className="tabla__codigo">{estudiante.codigo_estudiante}</span>,
    },
    {
      clave: 'nombres',
      etiqueta: 'Estudiante',
      render: (estudiante) => (
        <strong>
          {estudiante.nombres} {estudiante.apellidos}
        </strong>
      ),
    },
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
      clave: 'hora_ingreso',
      etiqueta: 'Hora de ingreso',
      render: (estudiante) => formatearHora(estudiante.hora_ingreso),
    },
    {
      clave: 'metodo_ingreso',
      etiqueta: 'Método',
      render: (estudiante) =>
        estudiante.metodo_ingreso ? descripcionEstado(estudiante.metodo_ingreso).etiqueta : '—',
    },
  ];

  const columnasHistorial: ColumnaTabla<HistorialAsistencia>[] = [
    { clave: 'fecha', etiqueta: 'Fecha', render: (fila) => formatearFecha(fila.fecha) },
    { clave: 'hora_inicio_prevista', etiqueta: 'Hora prevista', render: (fila) => fila.hora_inicio_prevista },
    {
      clave: 'estado',
      etiqueta: 'Estado',
      render: (fila) => (
        <Insignia tono={descripcionEstado(fila.estado).tono}>
          {descripcionEstado(fila.estado).etiqueta}
        </Insignia>
      ),
    },
    { clave: 'hora_ingreso', etiqueta: 'Hora de ingreso', render: (fila) => formatearHora(fila.hora_ingreso) },
    {
      clave: 'metodo_ingreso',
      etiqueta: 'Método',
      render: (fila) => (fila.metodo_ingreso ? descripcionEstado(fila.metodo_ingreso).etiqueta : '—'),
    },
  ];

  return (
    <div className="pagina">
      <Encabezado
        titulo="Asistencia"
        descripcion="Consulte las sesiones del día, revise el estado de cada estudiante y registre la asistencia."
        icono={<ClipboardCheck size={22} aria-hidden="true" />}
      />

      {error ? (
        <Aviso tono="peligro" titulo="No se pudieron cargar las sesiones">
          {error}
        </Aviso>
      ) : null}

      <Tarjeta
        titulo="Sesiones de hoy"
        descripcion="Seleccione una sesión para ver y modificar la asistencia de sus estudiantes."
        acciones={
          <button type="button" className="boton boton--secundario boton--pequeno" onClick={recargar}>
            Actualizar
          </button>
        }
      >
        {cargando ? (
          <Vacio titulo="Cargando sesiones…" />
        ) : sesiones.length === 0 ? (
          <Vacio
            titulo="No hay sesiones programadas hoy"
            descripcion="Genere el horario del día para poder registrar la asistencia."
          />
        ) : (
          <div className="rejilla rejilla--3">
            {sesiones.map((sesion: SesionClase) => (
              <button
                key={sesion.id_sesion_clase}
                type="button"
                className={`sesion ${idSesion === sesion.id_sesion_clase ? 'sesion--activa' : ''}`}
                onClick={() => setIdSesion(sesion.id_sesion_clase)}
              >
                <span className="sesion__curso">{sesion.curso}</span>
                <span className="sesion__horario">
                  <CalendarDays size={14} aria-hidden="true" /> {sesion.hora_inicio_prevista} -{' '}
                  {sesion.hora_fin_prevista}
                </span>
                <span className="sesion__conteos">
                  <span className="sesion__conteo sesion__conteo--exito">{sesion.asistencia.presentes} presentes</span>
                  <span className="sesion__conteo sesion__conteo--alerta">{sesion.asistencia.tardanzas} tardanzas</span>
                  <span className="sesion__conteo sesion__conteo--peligro">{sesion.asistencia.ausencias} ausencias</span>
                </span>
              </button>
            ))}
          </div>
        )}
      </Tarjeta>

      {sesion ? (
        <Tarjeta titulo={`Detalle de la sesión`} descripcion={mensajeSesion ?? undefined}>
          <div className="rejilla rejilla--4">
            <Estadistica
              etiqueta="Total"
              valor={sesion.asistencia.total}
              icono={<Users size={18} aria-hidden="true" />}
            />
            <Estadistica
              etiqueta="Presentes"
              valor={sesion.asistencia.presentes}
              tono="exito"
            />
            <Estadistica etiqueta="Tardanzas" valor={sesion.asistencia.tardanzas} tono="alerta" />
            <Estadistica etiqueta="Ausencias" valor={sesion.asistencia.ausencias} tono="peligro" />
          </div>

          <RegistroManual
            idSesion={sesion.id_sesion_clase}
            estudiantes={sesion.estudiantes}
            alRegistrar={() => {
              recargarDetalle();
              recargar();
            }}
          />

          <Tabla
            columnas={columnasEstudiantes}
            filas={sesion.estudiantes}
            claveFila={(estudiante) => estudiante.id_estudiante}
            cargando={cargandoDetalle}
            mensajeVacio="La sesión no tiene estudiantes inscritos"
          />
        </Tarjeta>
      ) : null}

      <Tarjeta
        titulo="Historial por estudiante"
        descripcion="Consulte los registros de asistencia de un estudiante en un período."
      >
        <div className="filtros">
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="estudiante-historial">
              N.º de estudiante
            </label>
            <input
              id="estudiante-historial"
              className="entrada"
              type="number"
              min={1}
              value={idEstudianteHistorial}
              onChange={(evento) => setIdEstudianteHistorial(evento.target.value)}
            />
          </div>
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="historial-desde">
              Desde
            </label>
            <input
              id="historial-desde"
              className="entrada"
              type="date"
              value={desde}
              onChange={(evento) => setDesde(evento.target.value)}
            />
          </div>
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="historial-hasta">
              Hasta
            </label>
            <input
              id="historial-hasta"
              className="entrada"
              type="date"
              value={hasta}
              onChange={(evento) => setHasta(evento.target.value)}
            />
          </div>
        </div>

        {errorHistorial ? (
          <Aviso tono="peligro" titulo="No se pudo cargar el historial">
            {errorHistorial}
          </Aviso>
        ) : null}

        <Tabla
          columnas={columnasHistorial}
          filas={historial}
          claveFila={(fila) => fila.id_asistencia}
          cargando={cargandoHistorial}
          mensajeVacio="Sin registros de asistencia"
          descripcionVacio="Indique el número de estudiante para ver su historial."
        />
      </Tarjeta>
    </div>
  );
}

interface PropiedadesRegistroManual {
  idSesion: number;
  estudiantes: EstudianteSesion[];
  alRegistrar: () => void;
}

function RegistroManual({ idSesion, estudiantes, alRegistrar }: PropiedadesRegistroManual) {
  const [idEstudiante, setIdEstudiante] = useState('');
  const [estado, setEstado] = useState<EstadoAsistencia>('presente');
  const [observacion, setObservacion] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [mensaje, setMensaje] = useState<{ tono: 'exito' | 'peligro'; texto: string } | null>(null);

  const registrar = async (evento: FormEvent<HTMLFormElement>): Promise<void> => {
    evento.preventDefault();
    setEnviando(true);
    setMensaje(null);
    try {
      const respuesta = await marcarManual(idSesion, {
        id_estudiante: Number(idEstudiante),
        estado,
        observacion: observacion.trim() ? observacion.trim() : undefined,
      });
      setMensaje({ tono: 'exito', texto: respuesta.mensaje });
      setObservacion('');
      alRegistrar();
    } catch (fallo) {
      setMensaje({ tono: 'peligro', texto: obtenerDetalleError(fallo).mensaje });
    } finally {
      setEnviando(false);
    }
  };

  return (
    <form className="formulario formulario--compacto formulario--en-linea" onSubmit={registrar}>
      <h3 className="formulario__titulo">
        <History size={16} aria-hidden="true" /> Registro manual
      </h3>
      {mensaje ? (
        <Aviso tono={mensaje.tono === 'exito' ? 'exito' : 'peligro'}>{mensaje.texto}</Aviso>
      ) : null}
      <div className="rejilla rejilla--3">
        <div className="campo">
          <label className="campo__etiqueta" htmlFor="manual-estudiante">
            Estudiante
          </label>
          <select
            id="manual-estudiante"
            className="entrada"
            value={idEstudiante}
            onChange={(evento) => setIdEstudiante(evento.target.value)}
            required
          >
            <option value="">Seleccione un estudiante</option>
            {estudiantes.map((estudiante) => (
              <option key={estudiante.id_estudiante} value={estudiante.id_estudiante}>
                {estudiante.codigo_estudiante} · {estudiante.nombres} {estudiante.apellidos}
              </option>
            ))}
          </select>
        </div>
        <div className="campo">
          <label className="campo__etiqueta" htmlFor="manual-estado">
            Estado
          </label>
          <select
            id="manual-estado"
            className="entrada"
            value={estado}
            onChange={(evento) => setEstado(evento.target.value as EstadoAsistencia)}
          >
            {ESTADOS_MANUALES.map((opcion) => (
              <option key={opcion.valor} value={opcion.valor}>
                {opcion.etiqueta}
              </option>
            ))}
          </select>
        </div>
        <div className="campo">
          <label className="campo__etiqueta" htmlFor="manual-observacion">
            Observación
          </label>
          <input
            id="manual-observacion"
            className="entrada"
            type="text"
            maxLength={500}
            value={observacion}
            onChange={(evento) => setObservacion(evento.target.value)}
          />
        </div>
      </div>
      <button type="submit" className="boton boton--primario" disabled={enviando}>
        {enviando ? 'Registrando…' : 'Registrar asistencia'}
      </button>
    </form>
  );
}

export default AttendancePage;
