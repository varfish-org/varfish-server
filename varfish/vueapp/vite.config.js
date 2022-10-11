const { resolve } = require('path')
import Vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import Components from 'unplugin-vue-components/vite'

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
  plugins: [
    Vue(),
    Components({
      resolvers: [IconsResolver()],
    }),
    Icons({
      autoInstall: true,
      compiler: 'vue3',
    }),
  ],
  resolve: {
    alias: {
      '@clinvarexport': resolve(__dirname, './src/clinvarexport'),
      '@variants': resolve(__dirname, './src/variants'),
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
