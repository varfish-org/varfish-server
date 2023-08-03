import App from '@cases/App.vue'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import CaseListApp from '@cases/components/CaseListApp.vue'
import CaseDetailApp from '@cases/components/CaseDetailApp.vue'
import FilterApp from '@variants/components/FilterApp.vue'
import VariantDetails from '@variants/components/VariantDetails.vue'
import SvFilterApp from '@svs/components/SvFilterApp.vue'
import SvDetails from '@svs/components/SvDetails.vue'
import { useHistoryStore } from '@varfish/stores/history'

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
    props: (route) => ({
      caseUuid: route.params.case,
    }),
  },
  {
    name: 'variants-filter',
    path: '/variants/filter/:case/:query?',
    component: FilterApp,
    props: (route) => ({
      caseUuid: route.params.case,
    }),
  },
  {
    name: 'variant-details',
    path: '/variants/details/:row/:selectedSection?',
    component: VariantDetails,
    props: (route) => ({
      resultRowUuid: route.params.row,
      selectedSection: route.params.selectedSection || 'genes',
    }),
  },
  {
    name: 'svs-filter',
    path: '/svs/filter/:case/:query?',
    component: SvFilterApp,
    props: (route) => ({
      caseUuid: route.params.case,
    }),
  },
  {
    name: 'sv-details',
    path: '/svs/details/:row/:selectedSection?',
    component: SvDetails,
    props: (route) => ({
      resultRowUuid: route.params.row,
      selectedSection: route.params.selectedSection || 'genes',
    }),
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (
      ['variant-details', 'sv-details'].includes(to.name) &&
      to.params.selectedSection
    ) {
      const res = { el: `#${to.params.selectedSection}` }
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

router.beforeEach((_to, from) => {
  // Push history element, initial will be swallowed by store.
  const historyStore = useHistoryStore()
  historyStore.pushPath(from)
})
