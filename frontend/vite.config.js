import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

const backendTarget = process.env.VITE_BACKEND_TARGET || 'http://localhost:5000';

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    // Allow requests from the specified host (fixes: Blocked request "srv.vm")
    allowedHosts: ['srv.vm'],
    host: true,
    proxy: {
      '/api': {
        target: backendTarget,
        changeOrigin: true
      }
    }
  }
});
