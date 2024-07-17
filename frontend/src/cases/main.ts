import App from '@/cases/App.vue'
import { createApp, nextTick } from 'vue'
import { registerPlugins } from './plugins'
import 'bootstrap'

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
