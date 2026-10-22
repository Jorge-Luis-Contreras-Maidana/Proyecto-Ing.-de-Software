import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './app/providers/AuthProvider';
import { AppRouter } from './app/router';
import { PantallaDeCarga } from './app/router';
import { Cargando } from './shared/ui';

/** Raíz de la aplicación. */
export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </AuthProvider>
  );
}

export { Cargando, PantallaDeCarga };
export default App;
