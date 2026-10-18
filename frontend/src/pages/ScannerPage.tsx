import React, { useEffect, useState } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { api } from '../services/api';

export const ScannerPage: React.FC = () => {
  const [scanResult, setScanResult] = useState<{ mensaje: string; estado: string; hora_ingreso?: string } | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const scanner = new Html5QrcodeScanner(
      'qr-reader',
      { fps: 10, qrbox: { width: 250, height: 250 } },
      /* verbose= */ false
    );

    const onScanSuccess = async (decodedText: string) => {
      try {
        const payload = JSON.parse(decodedText);
        if (payload.id_estudiante && payload.code) {
          scanner.clear();
          await registrarAsistencia(payload.id_estudiante, payload.code);
        }
      } catch {
        setErrorMsg('El formato del código QR escaneado es inválido.');
      }
    };

    scanner.render(onScanSuccess, (err) => {
      // Manejo silencioso de errores de frames no detectados
    });

    return () => {
      scanner.clear().catch(() => {});
    };
  }, []);

  const registrarAsistencia = async (idEstudiante: number, code: string) => {
    setLoading(true);
    setErrorMsg(null);
    setScanResult(null);

    try {
      const res = await api.post('/attendance/registrar', {
        id_estudiante: idEstudiante,
        codigo_qr: code,
      });
      setScanResult(res.data);
    } catch (err: any) {
      setErrorMsg(
        err.response?.data?.error?.mensaje ||
        err.response?.data?.mensaje ||
        'Error al registrar la asistencia'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '40px auto', padding: '20px', textAlign: 'center' }}>
      <h2>Registro de Asistencia mediante QR</h2>
      
      <div id="qr-reader" style={{ width: '100%', marginBottom: '20px' }}></div>

      {loading && <p>Procesando lectura...</p>}

      {scanResult && (
        <div style={{ padding: '15px', backgroundColor: '#d4edda', color: '#155724', borderRadius: '6px', marginTop: '15px' }}>
          <h3>{scanResult.mensaje}</h3>
          <p>Estado: <strong>{scanResult.estado}</strong></p>
          {scanResult.hora_ingreso && <p>Hora: {scanResult.hora_ingreso}</p>}
          <button onClick={() => window.location.reload()} style={{ padding: '8px 16px', marginTop: '10px' }}>
            Escanear Nuevo QR
          </button>
        </div>
      )}

      {errorMsg && (
        <div style={{ padding: '15px', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '6px', marginTop: '15px' }}>
          <p>{errorMsg}</p>
          <button onClick={() => window.location.reload()} style={{ padding: '8px 16px', marginTop: '10px' }}>
            Reintentar Lectura
          </button>
        </div>
      )}
    </div>
  );
};