import { createPinia } from 'pinia'
import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'

import App from './App.vue'
const CaseList = () => import('./components/CaseList.vue')
const CaseDetail = () => import('./components/CaseDetail.vue')
import { useCasesStore } from './stores/cases'

const routes = [
  {
    name: 'case-list',
    path: '/',
    component: CaseList,
    props: {
      currentTab: 'case-list',
    },
  },
  {
    name: 'case-list-qc',
    path: '/qc',
    component: CaseList,
    props: {
      currentTab: 'case-list-qc',
    },
  },
  {
    name: 'case-list-query-presets',
    path: '/query-presets',
    component: CaseList,
    props: {
      currentTab: 'case-list-query-presets',
      presetSet: 'factory-defaults',
    },
  },
  {
    name: 'case-list-query-presets-non-factory',
    path: '/query-presets/:presetSet',
    component: CaseList,
    props: (route) => ({
      currentTab: 'case-list-query-presets',
      presetSet: route.params.presetSet,
    }),
  },
  {
    name: 'case-detail',
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
