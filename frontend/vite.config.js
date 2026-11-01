import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Todo lo que el front pida a /api/... se reenvía a la API de Python (puerto 8000).
// Así el navegador cree que front y API están en el mismo lugar y no hace falta configurar CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        rewrite: (ruta) => ruta.replace(/^\/api/, ''),
      },
    },
  },
})
