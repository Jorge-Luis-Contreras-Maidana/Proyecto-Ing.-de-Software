import { UserX } from 'lucide-react';
import { descripcionEstado } from '../../../shared/lib/etiquetas';
import { formatearFecha, formatearFechaHora } from '../../../shared/lib/formatDate';
import { Aviso, Encabezado, Estadistica, Insignia, Tabla, Tarjeta } from '../../../shared/ui';
import type { ColumnaTabla } from '../../../shared/ui';
import { useInasistenciaDocente } from '../hooks/useAnnouncements';
import type { AvisoInasistenciaDocente } from '../types/announcements.types';

/** Avisos generados por la inasistencia de los docentes. */
export function InasistenciaDocentePage() {
  const { avisos, cargando, error } = useInasistenciaDocente();

  const pendientes = avisos.filter((aviso) => aviso.estado === 'pendiente').length;

  const columnas: ColumnaTabla<AvisoInasistenciaDocente>[] = [
    { clave: 'fecha_afectada', etiqueta: 'Fecha afectada', render: (aviso) => formatearFecha(aviso.fecha_afectada) },
    { clave: 'id_profesor', etiqueta: 'Docente', render: (aviso) => `N.º ${aviso.id_profesor}` },
    { clave: 'id_sesion_clase', etiqueta: 'Sesión', render: (aviso) => `N.º ${aviso.id_sesion_clase}` },
    { clave: 'motivo', etiqueta: 'Motivo' },
    {
      clave: 'estado',
      etiqueta: 'Estado',
      render: (aviso) => (
        <Insignia tono={descripcionEstado(aviso.estado).tono}>
          {descripcionEstado(aviso.estado).etiqueta}
        </Insignia>
      ),
    },
    { clave: 'enviado_en', etiqueta: 'Enviado', render: (aviso) => formatearFechaHora(aviso.enviado_en) },
    {
      clave: 'decision',
      etiqueta: 'Decisión',
      render: (aviso) => aviso.decision ?? '—',
    },
  ];

  return (
    <div className="pagina">
      <Encabezado
        titulo="Inasistencia docente"
        descripcion="Avisos generados cuando un docente no impartió la clase programada."
        icono={<UserX size={22} aria-hidden="true" />}
      />

      {error ? (
        <Aviso tono="peligro" titulo="No se pudieron cargar los avisos">
          {error}
        </Aviso>
      ) : null}

      <div className="rejilla rejilla--2">
        <Estadistica etiqueta="Avisos" valor={avisos.length} icono={<UserX size={18} aria-hidden="true" />} />
        <Estadistica etiqueta="Pendientes de revisión" valor={pendientes} tono="alerta" />
      </div>

      <Tarjeta>
        <Tabla
          columnas={columnas}
          filas={avisos}
          claveFila={(aviso) => aviso.id_aviso_docente}
          cargando={cargando}
          mensajeVacio="No hay avisos de inasistencia docente"
          descripcionVacio="Cuando se detecte la inasistencia de un docente aparecerá aquí."
        />
      </Tarjeta>
    </div>
  );
}

export default InasistenciaDocentePage;
