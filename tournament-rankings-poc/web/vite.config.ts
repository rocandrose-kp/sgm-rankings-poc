import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/sgm-rankings-poc/',
  server: {
    port: 3000,
  },
})
