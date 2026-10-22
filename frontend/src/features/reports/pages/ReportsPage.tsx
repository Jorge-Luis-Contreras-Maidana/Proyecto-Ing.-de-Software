import { useState } from 'react';
import { FileText } from 'lucide-react';
import { descripcionEstado } from '../../../shared/lib/etiquetas';
import { formatearFecha, formatearFechaHora } from '../../../shared/lib/formatDate';
import { nombreCompleto } from '../../../shared/lib/text';
import { Aviso as AvisoVisual, Encabezado, Estadistica, Insignia, Tarjeta, Tabla, Vacio, Ventana } from '../../../shared/ui';
import { useDetalleEstudiante, useReporteAsistencia, useReporteDiario, useResumen } from '../hooks/useReports';

type Pestana = 'resumen' | 'asistencia' | 'diario';

/** Reportes de asistencia de la unidad educativa. */
export function ReportsPage() {
  const [pestana, setPestana] = useState<Pestana>('resumen');
  const [desde, setDesde] = useState('');
  const [hasta, setHasta] = useState('');
  const [estudianteAbierto, setEstudianteAbierto] = useState<number | null>(null);

  const resumen = useResumen();
  const reporte = useReporteAsistencia({
    desde: desde || null,
    hasta: hasta || null,
  });
  const diario = useReporteDiario(null);
  const detalle = useDetalleEstudiante(estudianteAbierto);

  return (
    <div className="pagina">
      <Encabezado
        titulo="Reportes"
        descripcion="Indicadores de asistencia de la gestión activa, por curso, por estudiante y por día."
        icono={<FileText size={22} aria-hidden="true" />}
      />

      {resumen.error ? (
        <AvisoVisual tono="peligro" titulo="No se pudo cargar el resumen">
          {resumen.error}
        </AvisoVisual>
      ) : null}

      <div className="filtros">
        <div className="campo">
          <label className="campo__etiqueta" htmlFor="pestana-reporte">
            Vista
          </label>
          <select
            id="pestana-reporte"
            className="entrada"
            value={pestana}
            onChange={(evento) => setPestana(evento.target.value as Pestana)}
          >
            <option value="resumen">Resumen general</option>
            <option value="asistencia">Por estudiante</option>
            <option value="diario">Del día</option>
          </select>
        </div>
        {pestana === 'asistencia' ? (
          <>
            <div className="campo">
              <label className="campo__etiqueta" htmlFor="reporte-desde">
                Desde
              </label>
              <input
                id="reporte-desde"
                className="entrada"
                type="date"
                value={desde}
                onChange={(evento) => setDesde(evento.target.value)}
              />
            </div>
            <div className="campo">
              <label className="campo__etiqueta" htmlFor="reporte-hasta">
                Hasta
              </label>
              <input
                id="reporte-hasta"
                className="entrada"
                type="date"
                value={hasta}
                onChange={(evento) => setHasta(evento.target.value)}
              />
            </div>
          </>
        ) : null}
      </div>

      {pestana === 'resumen' ? (
        <>
          <div className="rejilla rejilla--3">
            <Estadistica
              etiqueta="Estudiantes"
              valor={resumen.resumen?.total_estudiantes ?? '—'}
              descripcion="Matrícula activa"
            />
            <Estadistica
              etiqueta="Asistencia"
              valor={`${resumen.resumen?.porcentaje_asistencia ?? 0}%`}
              tono="exito"
              descripcion="Presentes sobre el total"
            />
            <Estadistica
              etiqueta="Ausencias"
              valor={resumen.resumen?.ausencias ?? '—'}
              tono="peligro"
            />
            <Estadistica
              etiqueta="Tardanzas"
              valor={resumen.resumen?.tardanzas ?? '—'}
              tono="alerta"
            />
            <Estadistica
              etiqueta="Justificadas"
              valor={resumen.resumen?.justificadas ?? '—'}
              tono="info"
            />
            <Estadistica
              etiqueta="Clases"
              valor={resumen.resumen?.total_clases ?? '—'}
              descripcion="Sesiones registradas"
            />
          </div>

          <Tarjeta titulo="Por curso">
            <Tabla
              columnas={[
                { clave: 'curso', etiqueta: 'Curso' },
                { clave: 'presentes', etiqueta: 'Presentes', alineacion: 'derecha' },
                { clave: 'tardanzas', etiqueta: 'Tardanzas', alineacion: 'derecha' },
                { clave: 'ausencias', etiqueta: 'Ausencias', alineacion: 'derecha' },
                { clave: 'justificadas', etiqueta: 'Justificadas', alineacion: 'derecha' },
                {
                  clave: 'porcentaje_asistencia',
                  etiqueta: '% asistencia',
                  alineacion: 'derecha',
                  render: (fila) => `${fila.porcentaje_asistencia ?? 0}%`,
                },
              ]}
              filas={resumen.resumen?.por_curso ?? []}
              claveFila={(fila) => fila.id_curso}
              cargando={resumen.cargando}
              mensajeVacio="No hay datos de asistencia por curso."
            />
          </Tarjeta>
        </>
      ) : null}

      {pestana === 'asistencia' ? (
        <Tarjeta titulo="Asistencia por estudiante">
          {reporte.error ? (
            <AvisoVisual tono="peligro" titulo="No se pudo cargar el reporte">
              {reporte.error}
            </AvisoVisual>
          ) : null}
          <Tabla
            columnas={[
              {
                clave: 'nombres',
                etiqueta: 'Estudiante',
                render: (fila) => (
                  <button
                    type="button"
                    className="boton boton--fantasma boton--pequeno"
                    onClick={() => setEstudianteAbierto(fila.id_estudiante)}
                  >
                    {nombreCompleto(fila.nombres, fila.apellidos)}
                  </button>
                ),
              },
              { clave: 'codigo_estudiante', etiqueta: 'Código' },
              { clave: 'curso', etiqueta: 'Curso' },
              { clave: 'presentes', etiqueta: 'Presentes', alineacion: 'derecha' },
              { clave: 'tardanzas', etiqueta: 'Tardanzas', alineacion: 'derecha' },
              { clave: 'ausencias', etiqueta: 'Ausencias', alineacion: 'derecha' },
              {
                clave: 'porcentaje_asistencia',
                etiqueta: '% asistencia',
                alineacion: 'derecha',
                render: (fila) => `${fila.porcentaje_asistencia}%`,
              },
            ]}
            filas={reporte.filas}
            claveFila={(fila) => fila.id_estudiante}
            cargando={reporte.cargando}
            mensajeVacio="No hay registros para estos filtros."
          />
        </Tarjeta>
      ) : null}

      {pestana === 'diario' ? (
        <Tarjeta titulo="Asistencia del día">
          {diario.error ? (
            <AvisoVisual tono="peligro" titulo="No se pudo cargar el resumen del día">
              {diario.error}
            </AvisoVisual>
          ) : null}
          <Tabla
            columnas={[
              {
                clave: 'nombres',
                etiqueta: 'Estudiante',
                render: (fila) => nombreCompleto(fila.nombres, fila.apellidos),
              },
              { clave: 'fecha', etiqueta: 'Fecha', render: (fila) => formatearFecha(fila.fecha) },
              { clave: 'total_clases', etiqueta: 'Clases', alineacion: 'derecha' },
              { clave: 'presentes', etiqueta: 'Presentes', alineacion: 'derecha' },
              { clave: 'tardanzas', etiqueta: 'Tardanzas', alineacion: 'derecha' },
              { clave: 'ausencias', etiqueta: 'Ausencias', alineacion: 'derecha' },
            ]}
            filas={diario.filas}
            claveFila={(fila) => `${fila.id_estudiante}-${fila.fecha}`}
            cargando={diario.cargando}
            mensajeVacio="No hay asistencia registrada para hoy."
          />
        </Tarjeta>
      ) : null}

      {estudianteAbierto !== null ? (
        <Ventana
          abierto
          titulo="Detalle del estudiante"
          onCerrar={() => setEstudianteAbierto(null)}
          pie={
            <button type="button" className="boton boton--secundario" onClick={() => setEstudianteAbierto(null)}>
              Cerrar
            </button>
          }
        >
          {detalle.cargando ? (
            <Vacio titulo="Cargando detalle…" />
          ) : detalle.detalle ? (
            <div className="formulario">
              <dl className="lista-datos">
                <dt>Estudiante</dt>
                <dd>
                  {nombreCompleto(detalle.detalle.estudiante.nombres, detalle.detalle.estudiante.apellidos)}
                </dd>
                <dt>Código</dt>
                <dd>{detalle.detalle.estudiante.codigo_estudiante}</dd>
                <dt>Curso</dt>
                <dd>
                  {detalle.detalle.estudiante.curso
                    ? `${detalle.detalle.estudiante.curso.nivel} ${detalle.detalle.estudiante.curso.grado}${detalle.detalle.estudiante.curso.paralelo}`
                    : '—'}
                </dd>
                <dt>Asistencia</dt>
                <dd>{detalle.detalle.resumen.porcentaje_asistencia}%</dd>
              </dl>

              <h3>Por mes</h3>
              <Tabla
                columnas={[
                  { clave: 'mes', etiqueta: 'Mes' },
                  { clave: 'presentes', etiqueta: 'Presentes', alineacion: 'derecha' },
                  { clave: 'tardanzas', etiqueta: 'Tardanzas', alineacion: 'derecha' },
                  { clave: 'ausencias', etiqueta: 'Ausencias', alineacion: 'derecha' },
                ]}
                filas={detalle.detalle.por_mes}
                claveFila={(fila) => fila.mes}
                mensajeVacio="Sin datos por mes."
              />

              <h3>Últimos registros</h3>
              <Tabla
                columnas={[
                  { clave: 'fecha', etiqueta: 'Fecha', render: (fila) => formatearFecha(fila.fecha) },
                  { clave: 'curso', etiqueta: 'Curso' },
                  {
                    clave: 'estado',
                    etiqueta: 'Estado',
                    render: (fila) => (
                      <Insignia tono={descripcionEstado(fila.estado).tono}>
                        {descripcionEstado(fila.estado).etiqueta}
                      </Insignia>
                    ),
                  },
                  {
                    clave: 'hora_ingreso',
                    etiqueta: 'Ingreso',
                    render: (fila) => (fila.hora_ingreso ? formatearFechaHora(fila.hora_ingreso) : '—'),
                  },
                ]}
                filas={detalle.detalle.ultimas_lecturas}
                claveFila={(fila) => fila.id_asistencia}
                mensajeVacio="Sin registros de asistencia."
              />
            </div>
          ) : (
            <AvisoVisual tono="peligro">{detalle.error ?? 'No se encontró el detalle.'}</AvisoVisual>
          )}
        </Ventana>
      ) : null}
    </div>
  );
}

export default ReportsPage;
