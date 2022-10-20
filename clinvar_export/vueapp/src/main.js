import { createPinia } from 'pinia'
import { createApp } from 'vue'

// We need to import the CSS here or tree-shaking will remove it for the clinvarexport app.
import '@vueform/multiselect/themes/default.css'

import App from './App.vue'

const pinia = createPinia()
const app = createApp(App)
app.use(pinia)
app.mount('#app')
