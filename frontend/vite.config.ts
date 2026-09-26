import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy) => {
          proxy.on('error', (err: any, _req: any, res: any) => {
            // Gracefully handle backend startup / disconnection without unhandled proxy crash logs
            if (res && typeof res.writeHead === 'function' && !res.headersSent) {
              res.writeHead(503, {
                'Content-Type': 'application/json',
                'Retry-After': '2'
              });
              res.end(JSON.stringify({
                status: 'offline',
                message: 'KAVACH Backend is starting up or temporarily offline',
                code: err.code || 'ECONNREFUSED'
              }));
            }
          });
        }
      },
    },
  },
})
