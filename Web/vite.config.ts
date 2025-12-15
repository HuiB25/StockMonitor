import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/status': {
        target: 'http://localhost:8256',
        changeOrigin: true,
      },
      '/config': {
        target: 'http://localhost:8256',
        changeOrigin: true,
      },
    },
  },
})