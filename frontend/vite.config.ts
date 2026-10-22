
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl'
import { defineConfig, loadEnv } from 'vite'

/**
 * Hosts que el servidor de desarrollo acepta.
 *
 * Vite rechaza por seguridad las peticiones cuyo encabezado Host no conoce.
 * Sin esta lista, el túnel de ngrok y el acceso desde el celular en la red
 * local devolverían 403.
 *
 * El punto inicial significa "este dominio y cualquier subdominio": así
 * 'abdominal-onyx-consent.ngrok-free.dev' queda cubierto por
 * '.ngrok-free.dev', aunque ngrok cambie el nombre en cada arranque.
 */
const HOSTS_POR_DEFECTO = [
  'localhost',
  '127.0.0.1',
  '.ngrok-free.dev',
  '.ngrok.io',
  '.ngrok.app',
  '.ngrok-free.app',
  '.trycloudflare.com',
  '.loca.lt',
]

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  // El plugin SSL genera un certificado autofirmado. Es necesario para probar
  // el lector de QR desde el celular cuando se entra por la IP de la red.
  // Si el celular entra por el túnel de ngrok, el túnel ya sirve HTTPS y se
  // puede apagar con VITE_USE_SSL=false.
  const usarSsl = env.VITE_USE_SSL !== 'false'

  const permitidos = Array.from(
    new Set([
      ...HOSTS_POR_DEFECTO,
      ...(env.VITE_ALLOWED_HOSTS ?? '').split(',').map((host) => host.trim()).filter(Boolean),
    ])
  )

  return {
    plugins: [react(), ...(usarSsl ? [basicSsl()] : [])],
    server: {
      host: '0.0.0.0',
      allowedHosts: permitidos,
      proxy: {
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
