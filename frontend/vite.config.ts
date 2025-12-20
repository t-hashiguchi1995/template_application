import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        // Dockerコンテナ内からバックエンドにアクセスする場合は、サービス名を使用
        target: process.env.VITE_API_URL || 'http://backend:8800',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path, // パスをそのまま使用
      },
    },
  },
  preview: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        // Dockerコンテナ内からバックエンドにアクセスする場合は、サービス名を使用
        target: 'http://backend:8800',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path, // パスをそのまま使用
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, res) => {
            console.error('Proxy error:', err.message)
            if (!res.headersSent) {
              res.writeHead(500, {
                'Content-Type': 'text/plain'
              })
              res.end('Proxy error: ' + err.message)
            }
          })
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Proxying request:', req.method, req.url, 'to', proxyReq.path)
          })
        },
      },
    },
  },
})

