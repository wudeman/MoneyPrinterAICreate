import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        // 移除rewrite规则，保留完整的/api路径
        logLevel: 'debug',
        configure: (proxy, options) => {
          // 打印代理请求信息
          proxy.on('error', (err, req, res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('发送代理请求到:', proxyReq.path);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('从代理接收到响应:', proxyRes.statusCode);
          });
        }
      },
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})