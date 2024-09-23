import { VueQueryPlugin } from '@tanstack/vue-query'
import type { App } from 'vue'

import { router } from '../router'
import { client as _ } from './heyApi'
import { pinia } from './pinia'
import { setupBackendUrls } from './reevFrontend'
import { vuetify } from './vuetify'

export async function registerPlugins(app: App) {
  setupBackendUrls()
  app.use(pinia).use(vuetify).use(router).use(VueQueryPlugin)
}
