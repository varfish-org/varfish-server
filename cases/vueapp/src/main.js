import { createPinia } from 'pinia'
import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'

import App from './App.vue'
const CaseList = () => import('./components/CaseList.vue')
const CaseDetail = () => import('./components/CaseDetail.vue')
const FilterApp = () => import('@variants/components/FilterApp.vue')
const SvFilterApp = () => import('@svs/components/SvFilterApp.vue')
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
  {
    name: 'variants-filter',
    path: '/variants/filter/:case/:query?',
    component: FilterApp,
  },
  {
    name: 'variants-filter-details',
    path: '/variants/filter/:case/:query/:row/:selectedTab?',
    component: FilterApp,
    props: (route) => ({
      detailsModalVisible: true,
      detailsModalResultRowUuid: route.params.row,
      detailsModalSelectedTab: route.params.selectedTab || 'info',
    }),
  },
  {
    name: 'svs-filter',
    path: '/svs/filter/:case',
    component: SvFilterApp,
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
