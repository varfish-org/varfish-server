const { resolve } = require('path')
import Vue from '@vitejs/plugin-vue'
import IconsResolver from 'unplugin-icons/resolver'
import Icons from 'unplugin-icons/vite'
import Components from 'unplugin-vue-components/vite'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/static/vueapp/',
  build: {
    // generate manifest.json in outDir
    manifest: true,
    // overwrite default .html entry
    outDir: 'static/vueapp',
    rollupOptions: {
      input: {
        clinvarexport: resolve(__dirname, './src/clinvarexport/main.js'),
        cases: resolve(__dirname, './src/cases/main.js'),
        cohorts: resolve(__dirname, './src/cohorts/main.js'),
      },
    },
    target: 'es2020',
  },
  optimizeDeps: {
    esbuildOptions: {
      target: 'es2020',
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
      '@varfish': resolve(__dirname, './src/varfish'),
      '@variantsTest': resolve(__dirname, './tests/variants'),
      '@clinvarexport': resolve(__dirname, './src/clinvarexport'),
      '@variants': resolve(__dirname, './src/variants'),
      '@svs': resolve(__dirname, './src/svs'),
      '@cases': resolve(__dirname, './src/cases'),
      '@cases_qc': resolve(__dirname, './src/cases_qc'),
      '@cohorts': resolve(__dirname, './src/cohorts'),
    },
    preserveSymlinks: true,
  },
  test: {
    coverage: {
      all: true,
      // NB: (2022-22-08: c8 only gives 100% coverage for .vue)
      provider: 'istanbul',
      reporter: ['text', 'json', 'html'],
    },
    environment: 'happy-dom',
    include: [
      './tests/clinvarexport/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      './tests/variants/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      './tests/svs/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      './tests/cases/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      './tests/cases_qc/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      './tests/cohorts/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
    ],
    exclude: ['./static/**/*'],
  },
})
