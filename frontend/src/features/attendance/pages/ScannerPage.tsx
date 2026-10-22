import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react';
import { Html5Qrcode } from 'html5-qrcode';
import { Camera, CircleCheck, RefreshCw, ScanLine } from 'lucide-react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { descripcionEstado } from '../../../shared/lib/etiquetas';
import { formatearHora } from '../../../shared/lib/formatDate';
import { Aviso, Encabezado, Insignia, Tarjeta } from '../../../shared/ui';
import { registrarPorQr } from '../api/attendanceApi';
import { useSesionesDeHoy } from '../hooks/useAttendance';
import type { RegistroAsistencia } from '../types/attendance.types';

const ID_LECTOR = 'lector-qr-sesco';

/** Datos leídos del código QR de la credencial del estudiante. */
interface ContenidoCredencial {
  id_estudiante: number;
  code: string;
}

function leerCredencial(texto: string): ContenidoCredencial | null {
  try {
    const datos = JSON.parse(texto) as Partial<ContenidoCredencial>;
    if (typeof datos.id_estudiante === 'number' && typeof datos.code === 'string') {
      return { id_estudiante: datos.id_estudiante, code: datos.code };
    }
    return null;
  } catch {
    return null;
  }
}

/** Registro de asistencia mediante el lector de códigos QR. */
export function ScannerPage() {
  const { sesiones, cargando, error: errorSesiones } = useSesionesDeHoy();
  const [idSesion, setIdSesion] = useState<number | ''>('');
  const [escaneando, setEscaneando] = useState(true);
  const [errorLector, setErrorLector] = useState<string | null>(null);
  const [resultado, setResultado] = useState<RegistroAsistencia | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const [idEstudianteManual, setIdEstudianteManual] = useState('');
  const [codigoManual, setCodigoManual] = useState('');

  const lectorRef = useRef<Html5Qrcode | null>(null);
  const procesandoRef = useRef(false);

  const registrar = useCallback(
    async (idEstudiante: number, codigo: string): Promise<void> => {
      setEnviando(true);
      setError(null);
      setResultado(null);
      try {
        const respuesta = await registrarPorQr({
          id_estudiante: idEstudiante,
          codigo,
          id_sesion_clase: idSesion === '' ? null : idSesion,
        });
        setResultado(respuesta);
      } catch (fallo) {
        setError(obtenerDetalleError(fallo).mensaje);
      } finally {
        setEnviando(false);
      }
    },
    [idSesion]
  );

  // El lector de QR se crea una sola vez mientras la pantalla está activa.
  useEffect(() => {
    if (!escaneando) {
      return;
    }

    let vigente = true;
    let lector: Html5Qrcode | null = null;

    const iniciar = async (): Promise<void> => {
      // Si el contenedor no está en la página, no hay nada que escanear.
      if (!document.getElementById(ID_LECTOR)) {
        return;
      }
      try {
        lector = new Html5Qrcode(ID_LECTOR);
        lectorRef.current = lector;
        await lector.start(
          { facingMode: 'environment' },
          { fps: 10, qrbox: { width: 250, height: 250 } },
          (texto: string) => {
            if (procesandoRef.current) {
              return;
            }
            const credencial = leerCredencial(texto);
            if (!credencial) {
              setError('El código QR escaneado no corresponde a una credencial de estudiante.');
              return;
            }
            procesandoRef.current = true;
            void registrar(credencial.id_estudiante, credencial.code).finally(() => {
              procesandoRef.current = false;
            });
          },
          () => {
            // Los errores por fotograma sin código se ignoran.
          }
        );
        if (vigente) {
          setErrorLector(null);
        }
      } catch {
        // Sin cámara (o sin permiso) el registro manual sigue disponible.
        if (vigente) {
          setErrorLector(
            'No se pudo encender la cámara. Revise los permisos del navegador o use el registro manual.'
          );
        }
      }
    };

    void iniciar();

    return () => {
      vigente = false;
      lectorRef.current = null;
      const activo = lector;
      if (!activo) {
        return;
      }
      try {
        const limpieza = activo.stop();
        if (limpieza && typeof limpieza.catch === 'function') {
          void limpieza.catch(() => undefined);
        }
      } catch {
        // Si el lector ya estaba detenido, no hay nada que limpiar.
      }
    };
  }, [escaneando, registrar]);

  const registrarManual = async (evento: FormEvent<HTMLFormElement>): Promise<void> => {
    evento.preventDefault();
    const id = Number(idEstudianteManual);
    if (!Number.isFinite(id) || id <= 0) {
      setError('Indique el número de identificación del estudiante.');
      return;
    }
    if (codigoManual.trim().length < 4) {
      setError('El código de la credencial debe tener al menos 4 caracteres.');
      return;
    }
    await registrar(id, codigoManual.trim());
  };

  const reiniciar = (): void => {
    setResultado(null);
    setError(null);
    setEscaneando(false);
    window.setTimeout(() => setEscaneando(true), 50);
  };

  return (
    <div className="pagina">
      <Encabezado
        titulo="Escáner de asistencia"
        descripcion="Registre el ingreso de los estudiantes leyendo su credencial QR."
        icono={<ScanLine size={22} aria-hidden="true" />}
      />

      {errorSesiones ? (
        <Aviso tono="peligro" titulo="No se pudieron cargar las sesiones de hoy">
          {errorSesiones}
        </Aviso>
      ) : null}

      <Tarjeta titulo="Sesión de clase" descripcion="Indique a qué clase se registra el ingreso.">
        <div className="campo">
          <label className="campo__etiqueta" htmlFor="sesion-escaneo">
            Sesión de hoy
          </label>
          <select
            id="sesion-escaneo"
            className="entrada"
            value={idSesion}
            onChange={(evento) => setIdSesion(evento.target.value === '' ? '' : Number(evento.target.value))}
            disabled={cargando}
          >
            <option value="">Clase en curso del estudiante (automático)</option>
            {sesiones.map((sesion) => (
              <option key={sesion.id_sesion_clase} value={sesion.id_sesion_clase}>
                {sesion.curso} · {sesion.hora_inicio_prevista} - {sesion.hora_fin_prevista}
              </option>
            ))}
          </select>
        </div>
      </Tarjeta>

      <div className="rejilla rejilla--2">
        <Tarjeta titulo="Lector de códigos" descripcion="Apunte la cámara a la credencial del estudiante.">
          {errorLector ? (
            <Aviso tono="alerta" titulo="Cámara no disponible">
              {errorLector}
            </Aviso>
          ) : null}

          {escaneando ? (
            <div id={ID_LECTOR} className="lector" />
          ) : (
            <div className="lector lector--apagado">
              <Camera size={28} aria-hidden="true" />
              <p>Lector detenido</p>
            </div>
          )}

          <button type="button" className="boton boton--secundario" onClick={reiniciar}>
            <RefreshCw size={16} aria-hidden="true" /> Reiniciar lector
          </button>
        </Tarjeta>

        <Tarjeta titulo="Resultado" descripcion="Estado del ingreso recién registrado.">
          {enviando ? (
            <Aviso tono="info">Registrando el ingreso…</Aviso>
          ) : null}

          {resultado ? (
            <div className={`resultado resultado--${resultado.estado}`}>
              <CircleCheck size={28} aria-hidden="true" />
              <div>
                <p className="resultado__estado">
                  <Insignia tono={descripcionEstado(resultado.estado).tono}>
                    {descripcionEstado(resultado.estado).etiqueta}
                  </Insignia>
                </p>
                <p className="resultado__mensaje">{resultado.mensaje}</p>
                <p className="resultado__detalle">
                  Hora de ingreso: {formatearHora(resultado.hora_ingreso)}
                  {resultado.minutos_retraso > 0 ? ` · ${resultado.minutos_retraso} min de retraso` : ''}
                </p>
                {resultado.ya_registrado ? (
                  <p className="resultado__detalle">El ingreso ya estaba registrado con anterioridad.</p>
                ) : null}
              </div>
            </div>
          ) : null}

          {error ? (
            <Aviso tono="peligro" titulo="No se pudo registrar el ingreso">
              {error}
            </Aviso>
          ) : null}

          {!resultado && !error && !enviando ? (
            <p className="texto-suave">
              Al leer la credencial del estudiante se mostrará aquí el estado de su ingreso.
            </p>
          ) : null}
        </Tarjeta>
      </div>

      <Tarjeta
        titulo="Registro manual por código"
        descripcion="Alternativa al lector para environments sin cámara disponible."
      >
        <form className="formulario formulario--en-linea" onSubmit={registrarManual}>
          <div className="rejilla rejilla--2">
            <div className="campo">
              <label className="campo__etiqueta" htmlFor="manual-id-estudiante">
                N.º de estudiante
              </label>
              <input
                id="manual-id-estudiante"
                className="entrada"
                type="number"
                min={1}
                value={idEstudianteManual}
                onChange={(evento) => setIdEstudianteManual(evento.target.value)}
                required
              />
            </div>
            <div className="campo">
              <label className="campo__etiqueta" htmlFor="manual-codigo">
                Código de la credencial
              </label>
              <input
                id="manual-codigo"
                className="entrada"
                type="text"
                minLength={4}
                maxLength={32}
                value={codigoManual}
                onChange={(evento) => setCodigoManual(evento.target.value)}
                required
              />
            </div>
          </div>
          <button type="submit" className="boton boton--primario" disabled={enviando}>
            Registrar ingreso
          </button>
        </form>
      </Tarjeta>
    </div>
  );
}

export default ScannerPage;
