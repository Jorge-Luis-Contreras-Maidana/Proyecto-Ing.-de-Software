import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Bell,
  CalendarCheck,
  ClipboardList,
  FileText,
  GraduationCap,
  LayoutDashboard,
  Megaphone,
  QrCode,
  ScanLine,
  ShieldCheck,
  Users,
} from 'lucide-react';
import { useAuth } from '../../auth/hooks/useAuth';
import { listarNotificaciones } from '../../notifications/api/notificationsApi';
import { useResumen } from '../../reports/hooks/useReports';
import { descripcionEstado } from '../../../shared/lib/etiquetas';
import { formatearFechaHora } from '../../../shared/lib/formatDate';
import { nombreCompleto } from '../../../shared/lib/text';
import type { Rol } from '../../../shared/types/common';
import { Aviso, Encabezado, Estadistica, Insignia, Tarjeta, Vacio } from '../../../shared/ui';

interface Enlace {
  ruta: string;
  texto: string;
  descripcion: string;
  icono: React.ReactNode;
  roles: Rol[];
}

const ENLACES: Enlace[] = [
  {
    ruta: '/escaner',
    texto: 'Escanear QR',
    descripcion: 'Registre el ingreso de un estudiante escaneando su credencial.',
    icono: <ScanLine size={20} aria-hidden="true" />,
    roles: ['director', 'profesor'],
  },
  {
    ruta: '/asistencia',
    texto: 'Asistencia',
    descripcion: 'Consulte las clases del día y el estado de cada estudiante.',
    icono: <CalendarCheck size={20} aria-hidden="true" />,
    roles: ['director', 'profesor'],
  },
  {
    ruta: '/estudiantes',
    texto: 'Estudiantes',
    descripcion: 'Busque estudiantes, consulte su ficha y registre observaciones.',
    icono: <Users size={20} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor'],
  },
  {
    ruta: '/mi-qr',
    texto: 'Mi credencial QR',
    descripcion: 'Muestre su credencial para registrar su ingreso.',
    icono: <QrCode size={20} aria-hidden="true" />,
    roles: ['estudiante'],
  },
  {
    ruta: '/consulta-qr',
    texto: 'Consultar credencial',
    descripcion: 'Consulte o renueve la credencial QR de un estudiante.',
    icono: <QrCode size={20} aria-hidden="true" />,
    roles: ['director', 'profesor'],
  },
  {
    ruta: '/justificaciones',
    texto: 'Justificaciones',
    descripcion: 'Presente o revise las justificaciones de ausencia.',
    icono: <ClipboardList size={20} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor'],
  },
  {
    ruta: '/seguimiento',
    texto: 'Seguimiento',
    descripcion: 'Revise las alertas de inasistencia y tardanzas.',
    icono: <ShieldCheck size={20} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor'],
  },
  {
    ruta: '/citas',
    texto: 'Citas',
    descripcion: 'Convoque y gestione las reuniones con los tutores.',
    icono: <GraduationCap size={20} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor'],
  },
  {
    ruta: '/avisos',
    texto: 'Avisos',
    descripcion: 'Consulte los comunicados de la unidad educativa.',
    icono: <Megaphone size={20} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor', 'estudiante'],
  },
  {
    ruta: '/notificaciones',
    texto: 'Notificaciones',
    descripcion: 'Vea lo que requiere su atención.',
    icono: <Bell size={20} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor', 'estudiante'],
  },
  {
    ruta: '/reportes',
    texto: 'Reportes',
    descripcion: 'Consulte los indicadores de asistencia.',
    icono: <FileText size={20} aria-hidden="true" />,
    roles: ['director', 'profesor'],
  },
];

/** Panel principal: resumen del estado de la unidad educativa. */
export function DashboardPage() {
  const { usuario, tieneRol } = useAuth();
  const puedeVerResumen = tieneRol('director', 'profesor');
  const resumen = useResumen(puedeVerResumen);
  const [noLeidas, setNoLeidas] = useState(0);
  const [fechaAcceso] = useState(() => new Date().toISOString());
  const [ultimas, setUltimas] = useState<{ id_notificacion: number; titulo: string; estado: string }[]>([]);

  useEffect(() => {
    let vigente = true;
    listarNotificaciones()
      .then((respuesta) => {
        if (vigente) {
          setNoLeidas(respuesta.no_leidas);
          setUltimas(respuesta.items.slice(0, 5));
        }
      })
      .catch(() => {
        // El panel se muestra igual aunque falle el contador.
        if (vigente) {
          setNoLeidas(0);
          setUltimas([]);
        }
      });
    return () => {
      vigente = false;
    };
  }, []);

  const accesos = ENLACES.filter((enlace) =>
    usuario ? enlace.roles.some((rol) => usuario.roles.includes(rol)) : false
  );

  return (
    <div className="pagina">
      <Encabezado
        titulo={`Hola, ${usuario?.nombres ?? ''}`}
        descripcion="Panel de control de la unidad educativa."
        icono={<LayoutDashboard size={22} aria-hidden="true" />}
      />

      {puedeVerResumen ? (
        <div className="rejilla rejilla--4">
          <Estadistica
            etiqueta="Asistencia"
            valor={`${resumen.resumen?.porcentaje_asistencia ?? 0}%`}
            tono="exito"
            descripcion="Presentes sobre el total"
          />
          <Estadistica etiqueta="Ausencias" valor={resumen.resumen?.ausencias ?? '—'} tono="peligro" />
          <Estadistica etiqueta="Tardanzas" valor={resumen.resumen?.tardanzas ?? '—'} tono="alerta" />
          <Estadistica
            etiqueta="Justificadas"
            valor={resumen.resumen?.justificadas ?? '—'}
            tono="info"
          />
        </div>
      ) : null}

      <Tarjeta titulo="Accesos" descripcion="Las secciones disponibles para su cuenta.">
        <div className="rejilla rejilla--3">
          {accesos.map((acceso) => (
            <Link key={acceso.ruta} to={acceso.ruta} className="boton boton--secundario">
              {acceso.icono}
              <span>
                <strong>{acceso.texto}</strong>
                <br />
                <span className="texto-suave">{acceso.descripcion}</span>
              </span>
            </Link>
          ))}
        </div>
      </Tarjeta>

      {tieneRol('director', 'profesor', 'tutor') ? (
        <Tarjeta
          titulo="Notificaciones recientes"
          acciones={
            <Link className="boton boton--fantasma boton--pequeno" to="/notificaciones">
              Ver todas
            </Link>
          }
        >
          {noLeidas > 0 ? (
            <Aviso tono="info">
              Tiene {noLeidas} notificación{noLeidas === 1 ? '' : 'es'} sin leer.
            </Aviso>
          ) : null}
          {ultimas.length === 0 ? (
            <Vacio titulo="Sin notificaciones" descripcion="No hay nada pendiente de su atención." />
          ) : (
            <ul className="lista-avisos">
              {ultimas.map((notificacion) => (
                <li key={notificacion.id_notificacion} className="lista-avisos__item">
                  <div className="lista-avisos__encabezado">
                    <Insignia tono={descripcionEstado(notificacion.estado).tono}>
                      {descripcionEstado(notificacion.estado).etiqueta}
                    </Insignia>
                  </div>
                  <p className="lista-avisos__titulo">{notificacion.titulo}</p>
                </li>
              ))}
            </ul>
          )}
        </Tarjeta>
      ) : null}

      {usuario ? (
        <Tarjeta titulo="Su cuenta">
          <dl className="lista-datos">
            <dt>Nombre</dt>
            <dd>{nombreCompleto(usuario.nombres, usuario.apellidos)}</dd>
            <dt>Usuario</dt>
            <dd>{usuario.nombre_usuario}</dd>
            <dt>Roles</dt>
            <dd>{usuario.roles.join(', ')}</dd>
            <dt>Último acceso</dt>
            <dd>{formatearFechaHora(fechaAcceso)}</dd>
          </dl>
        </Tarjeta>
      ) : null}
    </div>
  );
}

export default DashboardPage;
