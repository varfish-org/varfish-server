import CaseDetailApp from '@cases/components/CaseDetailApp.vue'
import CaseListApp from '@cases/components/CaseListApp.vue'
import StrucvarDetails from '@svs/views/StrucvarDetails/StrucvarDetails.vue'
import SvFilterApp from '@svs/components/SvFilterApp.vue'
import { useHistoryStore } from '@varfish/stores/history'
import FilterApp from '@variants/components/FilterApp.vue'
import SeqvarDetails from '@variants/views/SeqvarDetails/SeqvarDetails.vue'
import {
  RouteLocationNormalized,
  RouteLocationNormalizedLoaded,
  createRouter,
  createWebHashHistory,
  RouteRecordRaw,
} from 'vue-router'

const routes: RouteRecordRaw[] = [
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
    props: (route: RouteLocationNormalized) => ({
      currentTab: 'case-list-query-presets',
      presetSet: route.params.presetSet,
    }),
  },
  {
    name: 'case-detail-overview',
    path: '/detail/:case',
    component: CaseDetailApp,
    props: (route: RouteLocationNormalized) => ({
      caseUuid: route.params.case,
      currentTab: 'overview',
    }),
  },
  {
    name: 'case-detail-qc',
    path: '/detail/:case/qc',
    component: CaseDetailApp,
    props: (route: RouteLocationNormalized) => ({
      caseUuid: route.params.case,
      currentTab: 'qc',
    }),
  },
  {
    name: 'case-detail-annotation',
    path: '/detail/:case/annotation',
    component: CaseDetailApp,
    props: (route: RouteLocationNormalized) => ({
      caseUuid: route.params.case,
      currentTab: 'annotation',
    }),
  },
  {
    name: 'case-detail-browser',
    path: '/detail/:case/browser',
    component: CaseDetailApp,
    props: (route: RouteLocationNormalized) => ({
      caseUuid: route.params.case,
      currentTab: 'browser',
    }),
  },
  {
    name: 'variants-filter',
    path: '/variants/filter/:case',
    component: FilterApp,
    props: (route: RouteLocationNormalized) => ({
      caseUuid: route.params.case,
    }),
  },
  {
    name: 'seqvar-details',
    path: '/seqvar/details/:row/:selectedSection?',
    component: SeqvarDetails,
    props: (route: RouteLocationNormalized) => ({
      resultRowUuid: route.params.row,
      selectedSection: route.params.selectedSection || 'top',
    }),
  },
  {
    name: 'svs-filter',
    path: '/svs/filter/:case',
    component: SvFilterApp,
    props: (route: RouteLocationNormalized) => ({
      caseUuid: route.params.case,
    }),
  },
  {
    name: 'strucvar-details',
    path: '/strucvar/details/:row/:selectedSection?',
    component: StrucvarDetails,
    props: (route: RouteLocationNormalized) => ({
      resultRowUuid: route.params.row,
      selectedSection: route.params.selectedSection || 'top',
    }),
  },
]

export type _ScrollPositionNormalized = {
  behavior?: ScrollOptions['behavior']
  left: number
  top: number
}

export const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(
    to: RouteLocationNormalized,
    _from: RouteLocationNormalizedLoaded,
    savedPosition: null | _ScrollPositionNormalized,
  ) {
    if (
      ['seqvar-details', 'strucvar-details'].includes(String(to.name)) &&
      to.params.selectedSection
    ) {
      const res = { el: `#${to.params.selectedSection}` }
      document.querySelector(res.el)?.scrollIntoView()
      return res
    } else {
      return savedPosition || { left: 0, top: 0 }
    }
  },
})

router.beforeEach((_to, from) => {
  // Push history element, initial will be swallowed by store.
  const historyStore = useHistoryStore()
  historyStore.pushPath(from)
})
