import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy:{
      '/api': {
        target: 'http://localhost:8000', //backend dev server
        ///spoof origin to avoid CORS issues with cookies - browser will think request coming from same frontend server instead of backend server
        // makes host header in request match frontend server instead of backend server, allowing cookies to be sent and receveived
        changeOrigin: true,
        // remove /api prefix when forwarding request to backend - backend routes don't have '/api' prefix
        rewrite: (path)=> path.replace(/^\/api/,'') 
        
      }
    
    }
  }

})
