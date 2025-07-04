import path from 'path'
import { defineConfig, splitVendorChunkPlugin } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const isProduction = mode === 'production'
  
  return {
    plugins: [
      react({
        // Production optimizations
        babel: isProduction ? {
          plugins: [
            ['babel-plugin-react-remove-properties', { properties: ['data-testid'] }],
          ],
        } : undefined,
      }),
      splitVendorChunkPlugin(),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 3000,
      host: true,
      proxy: {
        '/api': {
          target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/ws': {
          target: process.env.VITE_WS_URL || 'ws://localhost:8000',
          ws: true,
          changeOrigin: true,
        }
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: !isProduction,
      minify: isProduction ? 'terser' : false,
      cssMinify: isProduction,
      target: ['es2020', 'chrome58', 'firefox57', 'safari11'],
      rollupOptions: {
        output: {
          // Enhanced chunk splitting for better caching
          manualChunks: {
            // Framework chunks
            'react-vendor': ['react', 'react-dom'],
            'react-router': ['react-router-dom'],
            
            // UI framework chunks
            'mui-core': ['@mui/material', '@mui/system'],
            'mui-icons': ['@mui/icons-material'],
            'mui-lab': ['@mui/lab'],
            'emotion': ['@emotion/react', '@emotion/styled'],
            
            // State management
            'redux': ['@reduxjs/toolkit', 'react-redux'],
            
            // Charts and visualization
            'charts': ['chart.js', 'react-chartjs-2'],
            
            // Forms and validation
            'forms': ['react-hook-form', '@hookform/resolvers', 'yup', 'zod'],
            
            // Utilities
            'utils': ['axios', 'date-fns', 'lodash-es'],
            
            // Real-time communication
            'socket': ['socket.io-client'],
            
            // File handling
            'media': ['react-webcam', 'react-dropzone'],
            
            // Query and notifications
            'query': ['@tanstack/react-query'],
            'notifications': ['notistack'],
          },
          chunkFileNames: isProduction ? 
            'assets/[name]-[hash].js' : 
            'assets/[name].js',
          entryFileNames: isProduction ? 
            'assets/[name]-[hash].js' : 
            'assets/[name].js',
          assetFileNames: isProduction ? 
            'assets/[name]-[hash].[ext]' : 
            'assets/[name].[ext]',
        }
      },
      terserOptions: isProduction ? {
        compress: {
          drop_console: true,
          drop_debugger: true,
          pure_funcs: ['console.log', 'console.info', 'console.debug'],
        },
        mangle: {
          safari10: true,
        },
        format: {
          comments: false,
        },
      } : undefined,
      // Bundle analysis
      reportCompressedSize: isProduction,
      chunkSizeWarningLimit: 1000,
    },
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
      __PROD__: isProduction,
    },
    esbuild: {
      drop: isProduction ? ['console', 'debugger'] : [],
    },
    // Optimize dependencies
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        '@mui/material',
        '@mui/icons-material',
        'chart.js',
        'react-chartjs-2',
      ],
    },
    // Performance monitoring
    experimental: {
      renderBuiltUrl(filename: string, { hostType }: { hostType: 'js' | 'css' | 'html' }) {
        if (hostType === 'js') {
          return { js: `/${filename}` }
        }
        return `/${filename}`
      }
    }
  }
})