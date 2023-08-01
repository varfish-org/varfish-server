<script setup>
import CaseListPaneCases from '@cases/components/CaseList/PaneCases.vue'
import CaseListPaneQc from '@cases/components/CaseList/PaneQc.vue'
import { useRouter } from 'vue-router'
import QueryPresets from '@variants/components/QueryPresets.vue'

const props = defineProps({
  currentTab: {
    type: String,
    default: 'case-list', // keep in sync with Tabs.caseList
  },
  presetSet: String,
})

/* We show/hide the tab panes with Vue via the router.
 *
 * This gives us the advantage of being able to control loading of data,
 * and we can use v-if to hide the tab panes.  Also, Bootstrap's tab panes
 * cannot be used with flex as d-flex implies 'display: flex !important'.
 * Navigation is done using the router.
 */

/** Tab selection options. */
const Tabs = Object.freeze({
  caseList: 'case-list',
  qc: 'case-list-qc',
  // annotations: 'annotations',  // TODO
  queryPresets: 'case-list-query-presets',
})

/** The router. */
const router = useRouter()

/** Update the current tab. */
const updateCurrentTab = (newValue) => {
  router.push({
    name: newValue,
  })
}
</script>

<template>
  <div class="d-flex flex-column flex-grow-1">
    <ul class="nav nav-tabs" id="cases-tab" role="tablist">
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: props.currentTab === Tabs.caseList }"
          role="button"
          @click="updateCurrentTab(Tabs.caseList)"
        >
          <i-mdi-format-list-bulleted-square />
          Case List
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: props.currentTab === Tabs.qc }"
          role="button"
          @click="updateCurrentTab(Tabs.qc)"
        >
          <i-mdi-chart-multiple />
          Quality Control
        </a>
      </li>
      <!--    <li class="nav-item">-->
      <!--      <a-->
      <!--        class="nav-link"-->
      <!--        id="anno-tab"-->
      <!--        data-toggle="tab"-->
      <!--        href="#annotation"-->
      <!--        role="tab"-->
      <!--        @click="updateCurrentTab(Tabs.annotations)"-->
      <!--      >-->
      <!--        <i-mdi-bookmark-multiple />-->
      <!--        Variant Annotation-->

      <!--        <span class="badge badge-pill badge-primary">TODO</span>-->
      <!--      </a>-->
      <!--    </li>-->
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: props.currentTab === Tabs.queryPresets }"
          role="button"
          @click="updateCurrentTab(Tabs.queryPresets)"
        >
          <i-mdi-filter-settings />
          Query Presets
        </a>
      </li>
    </ul>
    <div class="tab-content flex-grow-1 d-flex flex-column" id="cases-content">
      <div
        v-if="props.currentTab === Tabs.caseList"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        id="case-list"
        role="tabpanel"
      >
        <CaseListPaneCases />
      </div>

      <div
        v-if="props.currentTab === Tabs.qc"
        class="border border-top-0 tab-pane fade show active"
        role="tabpanel"
      >
        <CaseListPaneQc />
      </div>

      <!--    <div-->
      <!--      v-if="currentTab === Tabs.annotations"-->
      <!--      class="border border-top-0 tab-pane fade show"-->
      <!--      id="annotation"-->
      <!--      role="tabpanel"-->
      <!--    >-->
      <!--      <div class="row pt-3">-->
      <!--        <div class="col" id="annotation-content">TODO</div>-->
      <!--      </div>-->
      <!--    </div>-->

      <div
        v-if="props.currentTab === Tabs.queryPresets"
        class="border border-top-0 tab-pane fade show active"
        role="tabpanel"
      >
        <QueryPresets :preset-set="presetSet" />
      </div>
    </div>
  </div>
</template>
