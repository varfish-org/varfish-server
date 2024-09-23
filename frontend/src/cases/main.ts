import 'bootstrap'
import { createApp, nextTick } from 'vue'

import App from '@/cases/App.vue'

import { registerPlugins } from './plugins'

declare global {
  interface Window {
    _paq: any[]
  }
}

async function bootstrap() {
  const app = createApp(App)

  await registerPlugins(app)

  app.mount('#app')

  await nextTick()
  window._paq?.push(['trackPageView'])
}

bootstrap()
