import { useEffect, useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, LockKeyhole, UserRound } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import { Aviso, Cargando } from '../../../shared/ui';

/** Pantalla de acceso al sistema. */
export function LoginPage() {
  const { iniciarSesion, estaAutenticado, cargando } = useAuth();
  const navegar = useNavigate();

  const [nombreUsuario, setNombreUsuario] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [error, setError] = useState<string>('');
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    if (estaAutenticado) {
      navegar('/panel', { replace: true });
    }
  }, [estaAutenticado, navegar]);

  if (cargando) {
    return (
      <div className="ingreso">
        <Cargando texto="Verificando la sesión…" />
      </div>
    );
  }

  const enviar = async (evento: FormEvent<HTMLFormElement>): Promise<void> => {
    evento.preventDefault();
    setError('');
    setEnviando(true);

    try {
      await iniciarSesion({ nombre_usuario: nombreUsuario.trim(), contrasena });
      navegar('/panel', { replace: true });
    } catch (fallo) {
      setError(obtenerDetalleError(fallo).mensaje);
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="ingreso">
      <div className="ingreso__panel">
        <div className="ingreso__marca">
          <span className="ingreso__logo">
            <GraduationCap size={28} aria-hidden="true" />
          </span>
          <div>
            <h1 className="ingreso__titulo">SESCO</h1>
            <p className="ingreso__lema">Sistema Escolar de Control y Observación</p>
          </div>
        </div>

        <p className="ingreso__descripcion">
          Ingrese con su usuario institucional para registrar la asistencia y hacer seguimiento a los
          estudiantes.
        </p>

        {error ? (
          <Aviso tono="peligro" titulo="No se pudo iniciar sesión">
            {error}
          </Aviso>
        ) : null}

        <form className="formulario" onSubmit={enviar}>
          <div className="campo">
            <label className="campo__etiqueta" htmlFor="nombre-usuario">
              Usuario
            </label>
            <div className="campo__con-icono">
              <UserRound size={18} aria-hidden="true" />
              <input
                id="nombre-usuario"
                className="entrada"
                type="text"
                value={nombreUsuario}
                onChange={(evento) => setNombreUsuario(evento.target.value)}
                autoComplete="username"
                required
                autoFocus
              />
            </div>
          </div>

          <div className="campo">
            <label className="campo__etiqueta" htmlFor="contrasena">
              Contraseña
            </label>
            <div className="campo__con-icono">
              <LockKeyhole size={18} aria-hidden="true" />
              <input
                id="contrasena"
                className="entrada"
                type="password"
                value={contrasena}
                onChange={(evento) => setContrasena(evento.target.value)}
                autoComplete="current-password"
                required
              />
            </div>
          </div>

          <button type="submit" className="boton boton--primario boton--ancho" disabled={enviando}>
            {enviando ? 'Ingresando…' : 'Iniciar sesión'}
          </button>
        </form>

        <div className="ingreso__ayuda">
          <p className="ingreso__ayuda-titulo">Cuentas de demostración</p>
          <ul className="ingreso__ayuda-lista">
            <li>
              <strong>directora.mquispe</strong> — Dirección
            </li>
            <li>
              <strong>prof.cmamani</strong> — Docencia
            </li>
            <li>
              <strong>tutor1</strong> — Tutor
            </li>
            <li>
              <strong>estudiante1</strong> — Estudiante
            </li>
          </ul>
          <p className="ingreso__ayuda-nota">La contraseña de todas es Demo1234!</p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
