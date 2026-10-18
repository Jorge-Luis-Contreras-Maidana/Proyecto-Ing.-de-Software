import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', padding: '20px' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #eee', pb: '10px' }}>
        <h2>SESCO - Panel Principal</h2>
        <button onClick={logout} style={{ padding: '8px 12px', background: '#dc3545', color: 'white', border: 'none', borderRadius: '4px' }}>
          Cerrar Sesión
        </button>
      </header>

      <div style={{ marginTop: '20px' }}>
        <h3>Bienvenido, {user?.nombres} {user?.apellidos}</h3>
        <p>Rol(es): <strong>{user?.roles.join(', ')}</strong></p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '30px' }}>
        {user?.roles.some((r) => ['director', 'profesor'].includes(r)) && (
          <Link to="/scanner" style={cardStyle}>
            📷 Escanear QR Asistencia
          </Link>
        )}

        {user?.roles.some((r) => ['estudiante', 'tutor'].includes(r)) && (
          <Link to="/my-qr" style={cardStyle}>
            📱 Ver mi QR Dinámico
          </Link>
        )}
      </div>
    </div>
  );
};

const cardStyle: React.CSSProperties = {
  padding: '20px',
  border: '1px solid #007bff',
  borderRadius: '8px',
  textAlign: 'center',
  textDecoration: 'none',
  color: '#007bff',
  fontWeight: 'bold',
  backgroundColor: '#f8f9fa',
};