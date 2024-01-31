import type { App } from 'vue'

import { router } from '../router'
import { vuetify } from './vuetify'
import { pinia } from '../stores'
import { setupBackendUrls } from './reevFrontend'

export async function registerPlugins(app: App) {
  setupBackendUrls()
  app.use(vuetify).use(router).use(pinia)
}
