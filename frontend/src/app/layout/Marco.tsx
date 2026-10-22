import { useState, type ReactNode } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import {
  Bell,
  CalendarCheck,
  ClipboardList,
  FileText,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  Megaphone,
  QrCode,
  ScanLine,
  Settings,
  ShieldCheck,
  Users,
} from 'lucide-react';
import { useAuth } from '../../features/auth/hooks/useAuth';
import { useAutoLogout } from '../../shared/hooks/useAutoLogout';
import { iniciales, nombreCompleto } from '../../shared/lib/text';
import type { Rol } from '../../shared/types/common';
import { Aviso } from '../../shared/ui';

interface Enlace {
  ruta: string;
  texto: string;
  icono: ReactNode;
  roles: Rol[];
}

const ENLACES: Enlace[] = [
  {
    ruta: '/panel',
    texto: 'Panel',
    icono: <LayoutDashboard size={16} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor', 'estudiante'],
  },
  {
    ruta: '/escaner',
    texto: 'Escáner',
    icono: <ScanLine size={16} aria-hidden="true" />,
    roles: ['director', 'profesor'],
  },
  {
    ruta: '/asistencia',
    texto: 'Asistencia',
    icono: <CalendarCheck size={16} aria-hidden="true" />,
    roles: ['director', 'profesor'],
  },
  {
    ruta: '/estudiantes',
    texto: 'Estudiantes',
    icono: <Users size={16} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor'],
  },
  {
    ruta: '/mi-qr',
    texto: 'Mi QR',
    icono: <QrCode size={16} aria-hidden="true" />,
    roles: ['estudiante'],
  },
  {
    ruta: '/consulta-qr',
    texto: 'Consultar QR',
    icono: <QrCode size={16} aria-hidden="true" />,
    roles: ['director', 'profesor'],
  },
  {
    ruta: '/justificaciones',
    texto: 'Justificaciones',
    icono: <ClipboardList size={16} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor'],
  },
  {
    ruta: '/seguimiento',
    texto: 'Seguimiento',
    icono: <ShieldCheck size={16} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor'],
  },
  {
    ruta: '/citas',
    texto: 'Citas',
    icono: <GraduationCap size={16} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor'],
  },
  {
    ruta: '/avisos',
    texto: 'Avisos',
    icono: <Megaphone size={16} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor', 'estudiante'],
  },
  {
    ruta: '/notificaciones',
    texto: 'Notificaciones',
    icono: <Bell size={16} aria-hidden="true" />,
    roles: ['director', 'profesor', 'tutor', 'estudiante'],
  },
  {
    ruta: '/reportes',
    texto: 'Reportes',
    icono: <FileText size={16} aria-hidden="true" />,
    roles: ['director', 'profesor'],
  },
  {
    ruta: '/configuracion',
    texto: 'Configuración',
    icono: <Settings size={16} aria-hidden="true" />,
    roles: ['director'],
  },
  {
    ruta: '/auditoria',
    texto: 'Auditoría',
    icono: <ShieldCheck size={16} aria-hidden="true" />,
    roles: ['director'],
  },
];

/** Marco de la aplicación: barra superior con el menú y los datos de la cuenta. */
export function Marco({ children }: { children: ReactNode }) {
  const { usuario, cerrarSesion, minutosInactividad } = useAuth();
  const ubicacion = useLocation();
  const [saliendo, setSaliendo] = useState(false);
  const [avisoInactividad, setAvisoInactividad] = useState<string | null>(null);

  useAutoLogout({
    minutosInactividad,
    alAdvertir: (segundosRestantes) => {
      setAvisoInactividad(
        `Su sesión se cerrará en ${segundosRestantes} segundos por inactividad. Guarde su trabajo.`
      );
    },
    alExpirar: () => {
      setAvisoInactividad(null);
      void cerrarSesion();
    },
  });

  const enlaces = ENLACES.filter((enlace) =>
    usuario ? enlace.roles.some((rol) => usuario.roles.includes(rol)) : false
  );

  const cerrar = async (): Promise<void> => {
    setSaliendo(true);
    try {
      await cerrarSesion();
    } finally {
      setSaliendo(false);
    }
  };

  return (
    <div className="marco">
      <header className="marco__barra">
        <Link to="/panel" className="marco__marca">
          <GraduationCap size={20} aria-hidden="true" /> SESCO
        </Link>

        <nav className="marco__nav" aria-label="Secciones de la aplicación">
          {enlaces.map((enlace) => (
            <NavLink
              key={enlace.ruta}
              to={enlace.ruta}
              className={({ isActive }) =>
                `marco__enlace ${isActive || ubicacion.pathname === enlace.ruta ? 'marco__enlace--activo' : ''}`
              }
            >
              {enlace.icono}
              {enlace.texto}
            </NavLink>
          ))}
        </nav>

        {usuario ? (
          <div className="marco__perfil">
            <span className="marco__avatar" aria-hidden="true">
              {iniciales(usuario.nombres, usuario.apellidos)}
            </span>
            <span className="marco__usuario">
              <span className="marco__nombre">{nombreCompleto(usuario.nombres, usuario.apellidos)}</span>
              <span className="marco__roles">{usuario.roles.join(', ')}</span>
            </span>
            <button
              type="button"
              className="boton boton--secundario boton--pequeno"
              onClick={() => void cerrar()}
              disabled={saliendo}
            >
              <LogOut size={14} aria-hidden="true" /> Salir
            </button>
          </div>
        ) : null}
      </header>

      <main className="marco__contenido">
        {avisoInactividad ? (
          <div className="pagina" style={{ paddingBottom: 0 }}>
            <Aviso tono="alerta">{avisoInactividad}</Aviso>
          </div>
        ) : null}
        {children}
      </main>
    </div>
  );
}

export default Marco;
