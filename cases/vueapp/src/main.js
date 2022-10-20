import { createPinia } from 'pinia'
import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'

import App from './App.vue'
const CaseList = () => import('./components/CaseList.vue')
const CaseDetail = () => import('./components/CaseDetail.vue')
import { useCasesStore } from './stores/cases'

const routes = [
  {
    path: '/',
    component: CaseList,
  },
  {
    path: '/detail/:case',
    component: CaseDetail,
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

const pinia = createPinia()
const app = createApp(App)
app.use(router)
app.use(pinia)
app.mount('#app')

const rawAppContext = JSON.parse(
  document.getElementById('sodar-ss-app-context').getAttribute('app-context') ||
    '{}'
)

const casesStore = useCasesStore()
casesStore.initialize(rawAppContext)
