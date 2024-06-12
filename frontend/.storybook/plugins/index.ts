import type { App } from 'vue'

import { router } from './router'
import { vuetify } from './vuetify'

export async function registerPlugins(app: App) {
  app.use(vuetify).use(router)
}
