import { fileURLToPath, URL } from 'url'
const { resolve } = require('path')
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    // generate manifest.json in outDir
    manifest: true,
    // overwrite default .html entry
    outDir: 'static/vueapp',
    rollupOptions: {
      input: {
        clinvarexport: resolve(__dirname, './src/clinvarexport/main.js'),
        variants: resolve(__dirname, './src/variants/main.js'),
      },
    },
  },
  plugins: [vue()],
  resolve: {
    alias: {
      '@clinvarexport': fileURLToPath(
        new URL('./src/clinvarexport', import.meta.url)
      ),
      '@variants': fileURLToPath(new URL('./src/variants', import.meta.url)),
    },
    preserveSymlinks: true,
  },
  test: {
    coverage: {
      all: true,
      provider: 'istanbul',
      reporter: ['text', 'json', 'html'],
    },
    environment: 'happy-dom',
    include: [
      './tests/clinvarexport/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      './tests/variants/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
    ],
  },
})
