import { useEffect, useRef, useState } from 'react';
import { QrCode, RefreshCw } from 'lucide-react';
import { useAuth } from '../../auth/hooks/useAuth';
import { formatearCuentaAtras } from '../../../shared/lib/formatDate';
import { Aviso, Cargando, Encabezado, Tarjeta } from '../../../shared/ui';
import { useMiCredencial } from '../hooks/useQr';

/** Credencial QR personal del estudiante. */
export function QrPage() {
  const { usuario } = useAuth();
  const { credencial, cargando, error, recargar } = useMiCredencial();
  const [segundosRestantes, setSegundosRestantes] = useState(0);
  const [expiraEn, setExpiraEn] = useState<number>(0);
  const renovando = useRef(false);

  // Al llegar la credencial se calcula cuándo vence y se reinicia la cuenta atrás.
  useEffect(() => {
    if (credencial) {
      setSegundosRestantes(credencial.expira_en_segundos);
      setExpiraEn(Date.now() + credencial.expira_en_segundos * 1000);
      renovando.current = false;
    }
  }, [credencial]);

  // La cuenta atrás se recalcula contra la hora de expiración.
  useEffect(() => {
    if (expiraEn === 0) {
      return;
    }
    const intervalo = window.setInterval(() => {
      setSegundosRestantes(Math.max(0, Math.round((expiraEn - Date.now()) / 1000)));
    }, 500);
    return () => window.clearInterval(intervalo);
  }, [expiraEn]);

  // Cuando el código vence se pide uno nuevo, una sola vez por credencial.
  useEffect(() => {
    if (!credencial || expiraEn === 0 || Date.now() < expiraEn || renovando.current) {
      return;
    }
    renovando.current = true;
    recargar();
  }, [credencial, expiraEn, recargar]);

  return (
    <div className="pagina">
      <Encabezado
        titulo="Mi credencial QR"
        descripcion="Muestre este código al personal de la unidad educativa para registrar su ingreso."
        icono={<QrCode size={22} aria-hidden="true" />}
      />

      {error ? (
        <Aviso tono="peligro" titulo="No se pudo obtener la credencial">
          {error}
        </Aviso>
      ) : null}

      <Tarjeta>
        {cargando && !credencial ? (
          <Cargando texto="Generando la credencial…" />
        ) : credencial ? (
          <div className="credencial">
            <div className="credencial__imagen">
              <img src={credencial.imagen} alt={`Código QR de ${usuario?.nombres ?? 'estudiante'}`} />
            </div>
            <div className="credencial__datos">
              <p className="credencial__nombre">
                {usuario?.nombres} {usuario?.apellidos}
              </p>
              <p className="credencial__codigo">
                Código: <strong>{credencial.codigo}</strong>
              </p>
              <p className="credencial__cuenta">
                Se renueva en <strong>{formatearCuentaAtras(segundosRestantes)}</strong>
              </p>
              <button type="button" className="boton boton--secundario" onClick={recargar}>
                <RefreshCw size={16} aria-hidden="true" /> Actualizar ahora
              </button>
            </div>
          </div>
        ) : (
          <p className="texto-suave">No hay credencial disponible para esta cuenta.</p>
        )}
      </Tarjeta>
    </div>
  );
}

export default QrPage;
