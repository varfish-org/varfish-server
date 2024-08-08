import StrucvarDetails from '@/svs/views/StrucvarDetails/StrucvarDetails.vue'
import StrucvarFilterLegacy from '@/svs/views/StrucvarFilterLegacy/StrucvarFilterLegacy.vue'
import { useHistoryStore } from '@/varfish/stores/history'
import SeqvarFilterLegacy from '@/variants/views/SeqvarFilterLegacy/SeqvarFilterLegacy.vue'
import SeqvarsQuery from '@/seqvars/views/SeqvarsQuery/SeqvarsQuery.vue'
import SeqvarDetails from '@/variants/views/SeqvarDetails/SeqvarDetails.vue'
import {
  RouteLocationNormalized,
  RouteLocationNormalizedLoaded,
  createRouter,
  createWebHistory,
  RouteRecordRaw,
} from 'vue-router'
import { nextTick } from 'vue'
import { useCtxStore } from '@/varfish/stores/ctx/store'
import { Tab as CaseListTab } from '@/cases/views/CaseList/types'

const CaseDetail = () => import('@/cases/views/CaseDetail/CaseDetail.vue')
const CaseList = () => import('@/cases/views/CaseList/CaseList.vue')
const SeqvarsPresetSets = () =>
  import('@/seqvars/views/PresetSets/PresetSets.vue')

const routes: RouteRecordRaw[] = [
  {
    name: 'case-list',
    path: '/-/cases/:project',
    component: CaseList,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      currentTab: CaseListTab.CASE_LIST,
    }),
  },
  {
    name: 'case-list-qc',
    path: '/-/cases/:project/qc',
    component: CaseList,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      currentTab: CaseListTab.QUALITY_CONTROL,
    }),
  },
  {
    name: 'case-list-query-presets',
    path: '/-/cases/:project/query-presets',
    component: CaseList,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      currentTab: CaseListTab.QUERY_PRESETS,
      presetSet: 'factory-defaults',
    }),
  },
  {
    name: 'case-list-query-presets-non-factory',
    path: '/-/cases/:project/query-presets/:presetSet',
    component: CaseList,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      currentTab: 'case-list-query-presets',
      presetSet: route.params.presetSet,
    }),
  },
  {
    name: 'seqvars-query-presets',
    path: '/-/seqvars/:project/query-presets/:presetSet?/:presetSetVersion?',
    component: SeqvarsPresetSets,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      presetSet: route.params.presetSet,
      presetSetVersion: route.params.presetSetVersion,
    }),
  },
  {
    name: 'case-detail-overview',
    path: '/-/cases/:project/detail/:case',
    component: CaseDetail,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      caseUuid: route.params.case,
      currentTab: 'overview',
    }),
  },
  {
    name: 'case-detail-qc',
    path: '/-/cases/:project/detail/:case/qc',
    component: CaseDetail,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      caseUuid: route.params.case,
      currentTab: 'qc',
    }),
  },
  {
    name: 'case-detail-annotation',
    path: '/-/cases/:project/detail/:case/annotation',
    component: CaseDetail,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      caseUuid: route.params.case,
      currentTab: 'annotation',
    }),
  },
  {
    name: 'case-detail-browser',
    path: '/-/cases/:project/detail/:case/browser',
    component: CaseDetail,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      caseUuid: route.params.case,
      currentTab: 'browser',
    }),
  },
  {
    name: 'seqvars-query',
    path: '/-/cases/:project/seqvars/querys/:case',
    component: SeqvarsQuery,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      caseUuid: route.params.case,
    }),
  },
  {
    name: 'variants-filter',
    path: '/-/cases/:project/variants/filter/:case',
    component: SeqvarFilterLegacy,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      caseUuid: route.params.case,
    }),
  },
  {
    name: 'seqvar-details',
    path: '/-/cases/:project/seqvar/details/:row/:selectedSection?',
    component: SeqvarDetails,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      resultRowUuid: route.params.row,
      selectedSection: route.params.selectedSection || 'top',
    }),
  },
  {
    name: 'svs-filter',
    path: '/-/cases/:project/svs/filter/:case',
    component: StrucvarFilterLegacy,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
      caseUuid: route.params.case,
    }),
  },
  {
    name: 'strucvar-details',
    path: '/-/cases/:project/strucvar/details/:row/:selectedSection?',
    component: StrucvarDetails,
    props: (route: RouteLocationNormalized) => ({
      projectUuid: route.params.project,
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
  history: createWebHistory(),
  routes,
  scrollBehavior(
    _to: RouteLocationNormalized,
    _from: RouteLocationNormalizedLoaded,
    savedPosition: null | _ScrollPositionNormalized,
  ) {
    return savedPosition || { left: 0, top: 0 }
  },
})

router.beforeEach(
  (to: RouteLocationNormalized, from: RouteLocationNormalizedLoaded) => {
    // Ensure that the CSRF token is set.
    const ctxStore = useCtxStore()
    ctxStore.initialize()

    // Push history element, initial will be swallowed by store.
    const historyStore = useHistoryStore()
    historyStore.pushPath(from)
  },
)

const DEFAULT_TITLE = 'VarFish'

router.afterEach((to) => {
  nextTick(() => {
    document.title = (to.meta.title as string) ?? DEFAULT_TITLE
  })
})
