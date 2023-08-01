import App from '@cases/App.vue'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
const CaseListApp = () => import('./components/CaseListApp.vue')
const CaseDetailApp = () => import('./components/CaseDetailApp.vue')
const FilterApp = () => import('@variants/components/FilterApp.vue')
const SvFilterApp = () => import('@svs/components/SvFilterApp.vue')
import { useCasesStore } from '@cases/stores/cases'

const routes = [
  {
    name: 'case-list',
    path: '/',
    component: CaseListApp,
    props: {
      currentTab: 'case-list',
    },
  },
  {
    name: 'case-list-qc',
    path: '/qc',
    component: CaseListApp,
    props: {
      currentTab: 'case-list-qc',
    },
  },
  {
    name: 'case-list-query-presets',
    path: '/query-presets',
    component: CaseListApp,
    props: {
      currentTab: 'case-list-query-presets',
      presetSet: 'factory-defaults',
    },
  },
  {
    name: 'case-list-query-presets-non-factory',
    path: '/query-presets/:presetSet',
    component: CaseListApp,
    props: (route) => ({
      currentTab: 'case-list-query-presets',
      presetSet: route.params.presetSet,
    }),
  },
  {
    name: 'case-detail',
    path: '/detail/:case',
    component: CaseDetailApp,
  },
  {
    name: 'variants-filter',
    path: '/variants/filter/:case/:query?',
    component: FilterApp,
  },
  {
    name: 'variants-filter-details',
    path: '/variants/filter-details/:case/:query/:row/:selectedTab?',
    component: FilterApp,
    props: (route) => ({
      detailsModalVisible: true,
      detailsModalResultRowUuid: route.params.row,
      detailsModalSelectedTab: route.params.selectedTab || 'link-outs',
    }),
  },
  {
    name: 'svs-filter',
    path: '/svs/filter/:case/:query?',
    component: SvFilterApp,
  },
  {
    name: 'svs-filter-details',
    path: '/svs/filter-details/:case/:query/:row/:selectedTab?',
    component: SvFilterApp,
    props: (route) => ({
      detailsModalVisible: true,
      detailsModalResultRowUuid: route.params.row,
      detailsModalSelectedTab: route.params.selectedTab || 'info',
    }),
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (
      ['variants-filter-details', 'svs-filter-details'].includes(to.name) &&
      to.params.selectedTab
    ) {
      const res = { el: `#${to.params.selectedTab}` }
      document.querySelector(res.el)?.scrollIntoView()
      return res
    } else {
      return savedPosition || { x: 0, y: 0 }
    }
  },
})

const pinia = createPinia()
const app = createApp(App)
app.use(router)
app.use(pinia)
app.mount('#app')

const rawAppContext = JSON.parse(
  document.getElementById('sodar-ss-app-context').getAttribute('app-context') ||
    '{}',
)

const casesStore = useCasesStore()
casesStore.initialize(rawAppContext)
