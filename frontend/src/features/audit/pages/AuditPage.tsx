import { useState } from 'react';
import { ScrollText } from 'lucide-react';
import { formatearFechaHora } from '../../../shared/lib/formatDate';
import { Aviso as AvisoVisual, Encabezado, Estadistica, Insignia, Tarjeta, Tabla, Paginacion } from '../../../shared/ui';
import { useAuditoria } from '../hooks/useAudit';

const OPERACIONES = [
  '',
  'CONSULTAR',
  'REGISTRAR_ASISTENCIA',
  'CREAR_ESTUDIANTE',
  'MODIFICAR_ESTUDIANTE',
  'DAR_DE_BAJA_ESTUDIANTE',
  'CREAR_OBSERVACION',
  'VINCULAR_TUTOR',
  'CONFIRMAR_TUTOR',
  'CREAR_NOTIFICACION',
  'CREAR_ALERTA',
  'CAMBIAR_ESTADO_ALERTA',
  'REVISAR_JUSTIFICACION',
  'CREAR_AVISO',
  'PUBLICAR_AVISO',
  'CREAR_CITACION',
];

const ENTIDADES = [
  '',
  'estudiantes',
  'asistencias',
  'observaciones_estudiante',
  'estudiante_tutor',
  'notificaciones',
  'alertas_asistencia',
  'citaciones',
  'avisos',
  'justificaciones_ausencia',
  'bitacora_auditoria',
];

/** Bitácora de auditoría: rastro de las operaciones del sistema. */
export function AuditPage() {
  const [operacion, setOperacion] = useState('');
  const [entidad, setEntidad] = useState('');
  const [desde, setDesde] = useState('');
  const [hasta, setHasta] = useState('');

  const { eventos, total, cargando, error, pagina, irAPagina } = useAuditoria({
    operacion: operacion || null,
    entidad: entidad || null,
    desde: desde || null,
    hasta: hasta || null,
  });

  const totalPaginas = Math.max(1, Math.ceil(total / 25));

  return (
    <div className="pagina">
      <Encabezado
        titulo="Auditoría"
        descripcion="Rastro de las operaciones sensibles realizadas en el sistema."
        icono={<ScrollText size={22} aria-hidden="true" />}
      />

      {error ? (
        <AvisoVisual tono="peligro" titulo="No se pudo cargar la bitácora">
          {error}
        </AvisoVisual>
      ) : null}

      <div className="rejilla rejilla--3">
        <Estadistica etiqueta="Eventos" valor={total} icono={<ScrollText size={18} aria-hidden="true" />} />
        <Estadistica etiqueta="Página" valor={pagina} descripcion={`de ${totalPaginas}`} />
      </div>

      <Tarjeta>
        <div className="filtros">
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="filtro-operacion">
              Operación
            </label>
            <select
              id="filtro-operacion"
              className="entrada"
              value={operacion}
              onChange={(evento) => setOperacion(evento.target.value)}
            >
              {OPERACIONES.map((valor) => (
                <option key={valor || 'todas'} value={valor}>
                  {valor === '' ? 'Todas' : valor.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="filtro-entidad">
              Entidad
            </label>
            <select
              id="filtro-entidad"
              className="entrada"
              value={entidad}
              onChange={(evento) => setEntidad(evento.target.value)}
            >
              {ENTIDADES.map((valor) => (
                <option key={valor || 'todas'} value={valor}>
                  {valor === '' ? 'Todas' : valor.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="filtro-audit-desde">
              Desde
            </label>
            <input
              id="filtro-audit-desde"
              className="entrada"
              type="date"
              value={desde}
              onChange={(evento) => setDesde(evento.target.value)}
            />
          </div>
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="filtro-audit-hasta">
              Hasta
            </label>
            <input
              id="filtro-audit-hasta"
              className="entrada"
              type="date"
              value={hasta}
              onChange={(evento) => setHasta(evento.target.value)}
            />
          </div>
        </div>

        <Tabla
          columnas={[
            { clave: 'fecha_hora', etiqueta: 'Fecha', render: (fila) => formatearFechaHora(fila.fecha_hora) },
            {
              clave: 'operacion',
              etiqueta: 'Operación',
              render: (fila) => <Insignia tono="neutro">{fila.operacion.replace(/_/g, ' ')}</Insignia>,
            },
            { clave: 'entidad', etiqueta: 'Entidad' },
            { clave: 'id_registro', etiqueta: 'Registro' },
            { clave: 'id_usuario', etiqueta: 'Usuario' },
            { clave: 'detalle', etiqueta: 'Detalle' },
          ]}
          filas={eventos}
          claveFila={(fila) => fila.id_evento}
          cargando={cargando}
          mensajeVacio="No hay eventos con estos filtros."
        />

        <Paginacion
          pagina={pagina}
          totalPaginas={totalPaginas}
          total={total}
          onCambioPagina={irAPagina}
        />
      </Tarjeta>
    </div>
  );
}

export default AuditPage;
