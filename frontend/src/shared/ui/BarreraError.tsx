import { Component, type ErrorInfo, type ReactNode } from 'react';

interface PropiedadesBarrera {
  children: ReactNode;
}

interface EstadoBarrera {
  error: Error | null;
}

/**
 * Evita que un fallo inesperado deje la pantalla en blanco.
 *
 * Si un componente lanza una excepción durante el renderizado, React la
 * propaga hacia arriba: sin esta barrera la persona usuaria vería una página
 * vacía sin ninguna explicación.
 */
export class BarreraError extends Component<PropiedadesBarrera, EstadoBarrera> {
  state: EstadoBarrera = { error: null };

  static getDerivedStateFromError(error: Error): EstadoBarrera {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('Error en la interfaz:', error, info.componentStack);
  }

  private reintentar = (): void => {
    this.setState({ error: null });
  };

  render(): ReactNode {
    const { error } = this.state;
    if (!error) {
      return this.props.children;
    }

    return (
      <div className="pagina">
        <div className="aviso aviso--peligro" role="alert">
          <div className="aviso__contenido">
            <strong className="aviso__titulo">Ocurrió un error en esta pantalla</strong>
            <div className="aviso__texto">
              <p>La operación no pudo completarse. Vuelva a intentarlo oActualice la página.</p>
              <p style={{ fontFamily: 'var(--fuente-mono)', fontSize: '0.8rem' }}>{error.message}</p>
            </div>
          </div>
          <div className="aviso__accion">
            <button type="button" className="boton boton--secundario boton--pequeno" onClick={this.reintentar}>
              Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }
}

export default BarreraError;
