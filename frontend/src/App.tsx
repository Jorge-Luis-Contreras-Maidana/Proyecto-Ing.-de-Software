import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ScannerPage } from './pages/ScannerPage';
import { StudentQrPage } from './pages/StudentQrPage';

// Componente para proteger rutas privadas
const PrivateRoute: React.FC<{ children: React.ReactNode; roles?: string[] }> = ({ children, roles }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) return <div>Cargando sesión...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (roles && user) {
    const tieneRol = user.roles.some((r) => roles.includes(r));
    if (!tieneRol) return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <DashboardPage />
              </PrivateRoute>
            }
          />

          <Route
            path="/scanner"
            element={
              <PrivateRoute roles={['director', 'profesor']}>
                <ScannerPage />
              </PrivateRoute>
            }
          />

          <Route
            path="/my-qr"
            element={
              <PrivateRoute roles={['estudiante', 'tutor']}>
                <StudentQrPage />
              </PrivateRoute>
            }
          />

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;