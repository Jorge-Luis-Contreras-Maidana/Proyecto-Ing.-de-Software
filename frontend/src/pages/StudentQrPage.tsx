import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

export const StudentQrPage: React.FC = () => {
  const [qrCodeData, setQrCodeData] = useState<string | null>(null);
  const [studentName, setStudentName] = useState<string>('');
  const [timeLeft, setTimeLeft] = useState<number>(20);

  const fetchQr = async () => {
    try {
      const res = await api.get('/qr/me/code');
      // Supone que el backend provee la cadena de la imagen o payload
      setQrCodeData(res.data.qr_image || res.data.code);
      setStudentName(res.data.nombre_estudiante || 'Estudiante');
      setTimeLeft(20);
    } catch (err) {
      console.error('Error al obtener el código QR', err);
    }
  };

  useEffect(() => {
    fetchQr();
    const interval = setInterval(() => {
      fetchQr();
    }, 20000); // Actualización cada 20s

    const timer = setInterval(() => {
      setTimeLeft((prev) => (prev > 1 ? prev - 1 : 20));
    }, 1000);

    return () => {
      clearInterval(interval);
      clearInterval(timer);
    };
  }, []);

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px', textAlign: 'center', border: '1px solid #ddd', borderRadius: '8px' }}>
      <h2>Credencial Escolar Digital</h2>
      <p>Estudiante: <strong>{studentName}</strong></p>

      {qrCodeData ? (
        <div style={{ margin: '20px 0' }}>
          <img src={qrCodeData} alt="Código QR Escolar" style={{ width: '220px', height: '220px' }} />
          <p style={{ fontSize: '14px', color: '#666' }}>
            Actualizando en: <strong>{timeLeft}s</strong>
          </p>
        </div>
      ) : (
        <p>Cargando código QR...</p>
      )}
    </div>
  );
};