import type { App } from 'vue'

import { router } from '../router'
import { vuetify } from './vuetify'
import { pinia } from './pinia'
import { client as _ } from './heyApi'
import { setupBackendUrls } from './reevFrontend'

export async function registerPlugins(app: App) {
  setupBackendUrls()
  app.use(pinia).use(vuetify).use(router)
}
