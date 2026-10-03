import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// No Docker, o backend é alcançado pelo nome do serviço e os arquivos montados
// precisam de polling para o hot reload funcionar.
const apiProxyTarget = process.env.API_PROXY_TARGET ?? 'http://localhost:8000'
const usePolling = process.env.VITE_USE_POLLING === 'true'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    watch: { usePolling },
    proxy: {
      '/api': apiProxyTarget,
    },
  },
})
