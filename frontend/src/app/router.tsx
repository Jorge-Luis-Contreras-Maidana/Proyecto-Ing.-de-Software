import { Navigate, Route, Routes } from 'react-router-dom';
import { Marco } from './layout/Marco';
import { RequiereSesion, RequireRole } from '../shared/guards/RequireRole';
import { Aviso, BarreraError, Cargando, Encabezado } from '../shared/ui';

import { LoginPage } from '../features/auth/pages/LoginPage';
import { DashboardPage } from '../features/dashboard/pages/DashboardPage';
import { StudentsPage } from '../features/students/pages/StudentsPage';
import { AttendancePage } from '../features/attendance/pages/AttendancePage';
import { ScannerPage } from '../features/attendance/pages/ScannerPage';
import { QrPage } from '../features/qr/pages/QrPage';
import { QrConsultaPage } from '../features/qr/pages/QrConsultaPage';
import { NotificationsPage } from '../features/notifications/pages/NotificationsPage';
import { AnnouncementsPage } from '../features/announcements/pages/AnnouncementsPage';
import { InasistenciaDocentePage } from '../features/announcements/pages/InasistenciaDocentePage';
import { FollowupPage } from '../features/followup/pages/FollowupPage';
import { MeetingsPage } from '../features/meetings/pages/MeetingsPage';
import { ReportsPage } from '../features/reports/pages/ReportsPage';
import { AuditPage } from '../features/audit/pages/AuditPage';
import { SettingsPage } from '../features/settings/pages/SettingsPage';
import { JustificationsPage } from '../features/justifications/pages/JustificationsPage';

/** Pantalla de error 404. */
function NoEncontrada() {
  return (
    <div className="pagina">
      <Encabezado
        titulo="Página no encontrada"
        descripcion="La dirección que abrió no corresponde a ninguna pantalla de SESCO."
      />
      <Aviso tono="alerta">Revise el enlace o vuelva al panel principal.</Aviso>
    </div>
  );
}

/** Pantalla que se muestra cuando la cuenta no tiene permiso para la sección. */
function SinPermiso() {
  return (
    <div className="pagina">
      <Encabezado titulo="Sin permisos" descripcion="Su cuenta no tiene acceso a esta sección." />
      <Aviso tono="peligro">
        Si cree que es un error, comuníquese con la dirección de la unidad educativa.
      </Aviso>
    </div>
  );
}

/** Rutas de la aplicación. */
export function AppRouter() {
  return (
    <BarreraError>
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/panel"
        element={
          <RequiereSesion>
            <Marco>
              <DashboardPage />
            </Marco>
          </RequiereSesion>
        }
      />

      <Route
        path="/escaner"
        element={
          <RequiereSesion>
            <RequireRole roles={['director', 'profesor']}>
              <Marco>
                <ScannerPage />
              </Marco>
            </RequireRole>
          </RequiereSesion>
        }
      />

      <Route
        path="/asistencia"
        element={
          <RequiereSesion>
            <RequireRole roles={['director', 'profesor']}>
              <Marco>
                <AttendancePage />
              </Marco>
            </RequireRole>
          </RequiereSesion>
        }
      />

      <Route
        path="/estudiantes"
        element={
          <RequiereSesion>
            <RequireRole roles={['director', 'profesor', 'tutor']}>
              <Marco>
                <StudentsPage />
              </Marco>
            </RequireRole>
          </RequiereSesion>
        }
      />

      <Route
        path="/mi-qr"
        element={
          <RequiereSesion>
            <RequireRole roles={['estudiante']}>
              <Marco>
                <QrPage />
              </Marco>
            </RequireRole>
          </RequiereSesion>
        }
      />

      <Route
        path="/consulta-qr"
        element={
          <RequiereSesion>
            <RequireRole roles={['director', 'profesor']}>
              <Marco>
                <QrConsultaPage />
              </Marco>
            </RequireRole>
          </RequiereSesion>
        }
      />

      <Route
        path="/justificaciones"
        element={
          <RequiereSesion>
            <RequireRole roles={['director', 'profesor', 'tutor']}>
              <Marco>
                <JustificationsPage />
              </Marco>
            </RequireRole>
          </RequiereSesion>
        }
      />

      <Route
        path="/seguimiento"
        element={
          <RequiereSesion>
            <RequireRole roles={['director', 'profesor', 'tutor']}>
              <Marco>
                <FollowupPage />
              </Marco>
            </RequireRole>
          </RequiereSesion>
        }
      />

      <Route
        path="/citas"
        element={
          <RequiereSesion>
            <RequireRole roles={['director', 'profesor', 'tutor']}>
              <Marco>
                <MeetingsPage />
              </Marco>
            </RequireRole>
          </RequiereSesion>
        }
      />

      <Route
        path="/avisos"
        element={
          <RequiereSesion>
            <Marco>
              <AnnouncementsPage />
            </Marco>
          </RequiereSesion>
        }
      />

      <Route
        path="/avisos-inasistencia-docente"
        element={
          <RequiereSesion>
            <RequireRole roles={['director', 'profesor']}>
              <Marco>
                <InasistenciaDocentePage />
              </Marco>
            </RequireRole>
          </RequiereSesion>
        }
      />

      <Route
        path="/notificaciones"
        element={
          <RequiereSesion>
            <Marco>
              <NotificationsPage />
            </Marco>
          </RequiereSesion>
        }
      />

      <Route
        path="/reportes"
        element={
          <RequiereSesion>
            <RequireRole roles={['director', 'profesor']}>
              <Marco>
                <ReportsPage />
              </Marco>
            </RequireRole>
          </RequiereSesion>
        }
      />

      <Route
        path="/configuracion"
        element={
          <RequiereSesion>
            <RequireRole roles={['director']}>
              <Marco>
                <SettingsPage />
              </Marco>
            </RequireRole>
          </RequiereSesion>
        }
      />

      <Route
        path="/auditoria"
        element={
          <RequiereSesion>
            <RequireRole roles={['director']}>
              <Marco>
                <AuditPage />
              </Marco>
            </RequireRole>
          </RequiereSesion>
        }
      />

      <Route path="/sin-permiso" element={<Marco><SinPermiso /></Marco>} />
      <Route path="/" element={<Navigate to="/panel" replace />} />
      <Route path="*" element={<Marco><NoEncontrada /></Marco>} />
    </Routes>
    </BarreraError>
  );
}

/** Carga inicial mientras se comprueba la sesión guardada. */
export function PantallaDeCarga() {
  return (
    <div className="pagina-carga">
      <Cargando texto="Abriendo SESCO…" />
    </div>
  );
}

export default AppRouter;
