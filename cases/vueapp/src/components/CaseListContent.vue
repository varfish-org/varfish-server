<script setup>
import { ref } from 'vue'
import CaseListPaneCases from './CaseListPaneCases.vue'
import CaseListPaneQc from './CaseListPaneQc.vue'

/* We show/hide the tab panes with Vue. This gives us the advantage of being
 * able to control loading of data, and we can use v-if to hide the tab panes.
 * Also, Bootstrap's tab panes cannot be used with flex as d-flex implies
 * 'display: flex !important'.
 */

/** Tab selection options. */
const Tabs = Object.freeze({
  caseList: 'case-list',
  qc: 'qc',
  annotations: 'annotations',
})

/** The currently selected tab. */
const currentTab = ref('case-list')

/** Update the current tab. */
const updateCurrentTab = (newValue) => {
  currentTab.value = newValue
}
</script>

<template>
  <div class="d-flex flex-column flex-grow-1">
    <ul class="nav nav-tabs" id="cases-tab" role="tablist">
      <li class="nav-item">
        <a
          class="nav-link active"
          id="case-list-tab"
          data-toggle="tab"
          href="#case-list"
          role="tab"
          @click="updateCurrentTab(Tabs.caseList)"
        >
          <i-mdi-format-list-bulleted-square />
          Case List
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          id="qc-tab"
          data-toggle="tab"
          href="#qc"
          role="tab"
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
    </ul>
    <div class="tab-content flex-grow-1 d-flex flex-column" id="cases-content">
      <div
        v-if="currentTab === Tabs.caseList"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        id="case-list"
        role="tabpanel"
      >
        <CaseListPaneCases />
      </div>

      <div
        v-if="currentTab === Tabs.qc"
        class="border border-top-0 tab-pane fade show"
        id="qc"
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
    </div>
  </div>
</template>
