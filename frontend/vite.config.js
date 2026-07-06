import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // dedicated port so the launcher script can find us; Vite still
    // auto-increments if it's taken
    port: 5178,
    proxy: {
      // same-origin in dev: /api/* is forwarded to FastAPI, so the browser
      // never makes a cross-origin request
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
