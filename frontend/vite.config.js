const { resolve } = require('path')
import Vue from '@vitejs/plugin-vue'
import IconsResolver from 'unplugin-icons/resolver'
import Icons from 'unplugin-icons/vite'
import Unfonts from 'unplugin-fonts/vite'
import Components from 'unplugin-vue-components/vite'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // The base assets URL depends on the mode.  For production, we need to
  // prefix it to the place where it is served by Django.
  const base = mode === 'production' ? '/static/vueapp/' : '/'

  return {
    base,
    build: {
      // generate .vite/manifest.json
      manifest: true,
      // include sourcemaps
      sourcemap: true,
      // overwrite default .html entry
      outDir: '../backend/varfish/static/vueapp',
      rollupOptions: {
        input: 'index.html',
        output: {
          globals: {
            jquery: 'window.$'
          }
        }
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
        dts: true,
        resolvers: [IconsResolver()],
      }),
      Icons({
        // autoInstall: true,
        compiler: 'vue3',
      }),
      Unfonts({
        google: {
          families: [
            {
              name: 'Roboto',
              styles: 'wght@100;300;400;500;700;900'
            }
          ]
        }
      })
    ],
    resolve: {
      alias: {
        '@test': resolve(__dirname, './tests/'),
        '@bihealth/reev-frontend-lib': resolve(__dirname, './ext/reev-frontend-lib/src'),
        '@varfish-org/varfish-api': resolve(__dirname, './ext/varfish-api/src'),
        '@varfish-org/viguno-api': resolve(__dirname, './ext/viguno-api/src'),
        '@': resolve(__dirname, './src/'),
      },
    },
    server: {
      origin: "http://127.0.0.1:3000",
      // The SPA lives at "/-/" and the index.html is served from Django.
      // vite serves some stuff from other prefixes. The remaining requests are
      // proxied to the backend.
      proxy: {
        '^\/(?!(-|@|src|node_modules|ext|favicon.ico)).*': {
          target: 'http://localhost:8000',
          changeOrigin: false,
          secure: false,
        }
      }
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
        './tests/variants/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
        './tests/svs/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
        './tests/cases/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
        './tests/cohorts/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
        './src/**/*.spec.ts',
      ],
      exclude: ['./static/**/*'],
    },
  }
})
