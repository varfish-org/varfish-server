const { resolve } = require('path')
import Vue from '@vitejs/plugin-vue'
import IconsResolver from 'unplugin-icons/resolver'
import Icons from 'unplugin-icons/vite'
import Components from 'unplugin-vue-components/vite'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    // generate manifest.json in outDir
    manifest: true,
    // overwrite default .html entry
    outDir: 'static/vueapp',
    rollupOptions: {
      output: {
        hoistTransitiveImports: false
      },
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
      '@stories': resolve(__dirname, './src/stories'),
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
