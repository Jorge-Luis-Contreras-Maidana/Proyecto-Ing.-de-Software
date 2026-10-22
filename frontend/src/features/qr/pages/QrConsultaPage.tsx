import { useState } from 'react';
import { IdCard, RefreshCw, Search } from 'lucide-react';
import { useAuth } from '../../auth/hooks/useAuth';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { normalizarTexto } from '../../../shared/lib/text';
import { useValorConRetraso } from '../../../shared/hooks/useValorConRetraso';
import { Aviso, Cargando, Encabezado, Insignia, Tabla, Tarjeta } from '../../../shared/ui';
import type { ColumnaTabla } from '../../../shared/ui';
import { renovarCredencial } from '../api/qrApi';
import { useCredencialDeEstudiante } from '../hooks/useQr';
import { useEstudiantes } from '../../students/hooks/useStudents';
import type { Estudiante } from '../../students/types/students.types';

/** Consulta y renovación de la credencial QR de un estudiante. */
export function QrConsultaPage() {
  const { tieneRol } = useAuth();
  const esDirector = tieneRol('director');

  const [busqueda, setBusqueda] = useState('');
  const busquedaRetrasada = useValorConRetraso(busqueda);
  const { estudiantes, cargando } = useEstudiantes({
    q: normalizarTexto(busquedaRetrasada),
    estado: 'todos',
    page: 1,
    per_page: 20,
  });

  const [idEstudiante, setIdEstudiante] = useState<number | null>(null);
  const { credencial, cargando: cargandoCredencial, error, recargar } = useCredencialDeEstudiante(idEstudiante);
  const [mensaje, setMensaje] = useState<{ tono: 'exito' | 'peligro'; texto: string } | null>(null);
  const [renovando, setRenovando] = useState(false);

  const renovar = async (): Promise<void> => {
    if (idEstudiante === null) {
      return;
    }
    setRenovando(true);
    setMensaje(null);
    try {
      await renovarCredencial(idEstudiante);
      setMensaje({ tono: 'exito', texto: 'Se emitió una credencial nueva para el estudiante.' });
      recargar();
    } catch (fallo) {
      setMensaje({ tono: 'peligro', texto: obtenerDetalleError(fallo).mensaje });
    } finally {
      setRenovando(false);
    }
  };

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
        <strong>
          {estudiante.nombres} {estudiante.apellidos}
        </strong>
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
    {
      clave: 'estado',
      etiqueta: 'Estado',
      render: (estudiante) => (
        <Insignia tono={estudiante.estado === 'activo' ? 'exito' : 'neutro'}>
          {estudiante.estado === 'activo' ? 'Activo' : estudiante.estado}
        </Insignia>
      ),
    },
    {
      clave: 'acciones',
      etiqueta: 'Credencial',
      alineacion: 'derecha',
      render: (estudiante) => (
        <button
          type="button"
          className="boton boton--secundario boton--pequeno"
          onClick={() => setIdEstudiante(estudiante.id_estudiante)}
        >
          Ver credencial
        </button>
      ),
    },
  ];

  return (
    <div className="pagina">
      <Encabezado
        titulo="Credenciales de estudiantes"
        descripcion="Consulte el código QR vigente de un estudiante y renueve la credencial cuando sea necesario."
        icono={<IdCard size={22} aria-hidden="true" />}
      />

      {mensaje ? (
        <Aviso tono={mensaje.tono === 'exito' ? 'exito' : 'peligro'}>{mensaje.texto}</Aviso>
      ) : null}

      <div className="rejilla rejilla--2">
        <Tarjeta titulo="Estudiantes">
          <div className="campo campo--buscador">
            <label className="campo__etiqueta" htmlFor="busqueda-credencial">
              Buscar
            </label>
            <div className="campo__con-icono">
              <Search size={18} aria-hidden="true" />
              <input
                id="busqueda-credencial"
                className="entrada"
                type="search"
                placeholder="Nombre o código"
                value={busqueda}
                onChange={(evento) => setBusqueda(evento.target.value)}
              />
            </div>
          </div>

          <Tabla
            columnas={columnas}
            filas={estudiantes}
            claveFila={(estudiante) => estudiante.id_estudiante}
            cargando={cargando}
            mensajeVacio="No hay estudiantes que coincidan con la búsqueda"
          />
        </Tarjeta>

        <Tarjeta titulo="Credencial seleccionada">
          {cargandoCredencial ? <Cargando texto="Obteniendo la credencial…" /> : null}

          {error ? (
            <Aviso tono="peligro" titulo="No se pudo obtener la credencial">
              {error}
            </Aviso>
          ) : null}

          {credencial ? (
            <div className="credencial">
              <div className="credencial__imagen">
                <img
                  src={credencial.imagen}
                  alt={`Código QR de ${credencial.nombres} ${credencial.apellidos}`}
                />
              </div>
              <div className="credencial__datos">
                <p className="credencial__nombre">
                  {credencial.nombres} {credencial.apellidos}
                </p>
                <p className="credencial__codigo">
                  {credencial.codigo_estudiante} · Código <strong>{credencial.codigo}</strong>
                </p>
                <p className="credencial__cuenta">
                  Credencial {credencial.credencial_activa ? 'activa' : 'inactiva'} · vence en{' '}
                  <strong>{credencial.expira_en_segundos}</strong> s
                </p>
                {esDirector ? (
                  <button
                    type="button"
                    className="boton boton--primario"
                    onClick={() => void renovar()}
                    disabled={renovando}
                  >
                    <RefreshCw size={16} aria-hidden="true" />
                    {renovando ? 'Renovando…' : 'Renovar credencial'}
                  </button>
                ) : (
                  <p className="texto-suave">Solo la dirección puede renovar una credencial.</p>
                )}
              </div>
            </div>
          ) : null}

          {!credencial && !cargandoCredencial && !error ? (
            <p className="texto-suave">Seleccione un estudiante para ver su credencial.</p>
          ) : null}
        </Tarjeta>
      </div>
    </div>
  );
}

export default QrConsultaPage;
