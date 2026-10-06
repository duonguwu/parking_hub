import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'prompt',
      includeAssets: [
        'favicon.svg',
        'pwa-192x192.png',
        'pwa-512x512.png',
        'maskable-icon-512x512.png',
        'apple-touch-icon.png',
      ],
      manifest: {
        id: '/app',
        name: 'Parking Hub - Nền Tảng Đỗ Xe Thông Minh',
        short_name: 'ParkingHub',
        description: 'Tìm kiếm bãi đỗ xe, đặt chỗ thông minh bằng AI, và quản lý bãi đỗ xe',
        theme_color: '#0284c7',
        background_color: '#f8fafc',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/app',
        icons: [
          {
            src: '/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any',
          },
          {
            src: '/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any',
          },
          {
            src: '/maskable-icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
          {
            src: '/apple-touch-icon.png',
            sizes: '180x180',
            type: 'image/png',
            purpose: 'any',
          },
        ],
        screenshots: [
          {
            src: '/screenshot-desktop.png',
            sizes: '1280x720',
            type: 'image/png',
            form_factor: 'wide',
            label: 'Bản đồ đỗ xe Parking Hub trên máy tính',
          },
          {
            src: '/screenshot-mobile.png',
            sizes: '750x1334',
            type: 'image/png',
            form_factor: 'narrow',
            label: 'Ứng dụng Parking Hub trên điện thoại di động',
          },
        ],
        shortcuts: [
          {
            name: 'Bản đồ đỗ xe',
            short_name: 'Bản đồ',
            description: 'Tìm kiếm và định vị bãi đỗ xe gần nhất',
            url: '/app/map',
            icons: [{ src: '/pwa-192x192.png', sizes: '192x192' }],
          },
          {
            name: 'Lịch hẹn gửi xe',
            short_name: 'Lịch hẹn',
            description: 'Xem các lượt đặt chỗ đang diễn ra',
            url: '/app/bookings',
            icons: [{ src: '/pwa-192x192.png', sizes: '192x192' }],
          },
          {
            name: 'Phương tiện của tôi',
            short_name: 'Xe của tôi',
            description: 'Quản lý danh sách phương tiện',
            url: '/app/vehicles',
            icons: [{ src: '/pwa-192x192.png', sizes: '192x192' }],
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,ico,woff,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/.*\.tile\.openstreetmap\.org\/.*/i,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'osm-tiles-cache',
              expiration: {
                maxEntries: 500,
                maxAgeSeconds: 60 * 60 * 24 * 30, // 30 days
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          {
            urlPattern: /^https:\/\/images\.unsplash\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'unsplash-images-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 7, // 7 days
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
        ],
      },
      devOptions: {
        enabled: true,
        type: 'module',
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    allowedHosts: true,
    proxy: {
      '/auth': { target: 'http://localhost:8000', changeOrigin: true },
      '/customer': { target: 'http://localhost:8000', changeOrigin: true },
      '/garage-portal': { target: 'http://localhost:8000', changeOrigin: true },
      '/admin-portal': { target: 'http://localhost:8000', changeOrigin: true },
      '/match': { target: 'http://localhost:8000', changeOrigin: true },
      '/bookings': { target: 'http://localhost:8000', changeOrigin: true },
      '/notifications': { target: 'http://localhost:8000', changeOrigin: true },
      '/health': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
  preview: {
    port: 5173,
    allowedHosts: true,
    proxy: {
      '/auth': { target: 'http://localhost:8000', changeOrigin: true },
      '/customer': { target: 'http://localhost:8000', changeOrigin: true },
      '/garage-portal': { target: 'http://localhost:8000', changeOrigin: true },
      '/admin-portal': { target: 'http://localhost:8000', changeOrigin: true },
      '/match': { target: 'http://localhost:8000', changeOrigin: true },
      '/bookings': { target: 'http://localhost:8000', changeOrigin: true },
      '/notifications': { target: 'http://localhost:8000', changeOrigin: true },
      '/health': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
  build: {
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-leaflet': ['leaflet', 'react-leaflet'],
          'vendor-icons': ['lucide-react'],
        },
      },
    },
  },
})


