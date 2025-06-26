import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'static/dist',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'js/[name].[hash].js',
        chunkFileNames: 'js/[name].[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.') || []
          const extType = info[info.length - 1]
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
            return `images/[name].[hash][extname]`
          }
          if (/css/i.test(extType)) {
            return `css/[name].[hash][extname]`
          }
          return `assets/[name].[hash][extname]`
        }
      }
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/auth': 'http://localhost:5006',
      '/api': 'http://localhost:5006'
    }
  }
})