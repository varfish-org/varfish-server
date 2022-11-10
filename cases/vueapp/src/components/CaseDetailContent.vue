<script setup>
import { computed, ref } from 'vue'

import CaseDetailPaneCase from './CaseDetailPaneCase.vue'
import CaseDetailPaneQc from './CaseDetailPaneQc.vue'
import CaseDetailPaneAnnotations from './CaseDetailPaneAnnotations.vue'
import { useCaseDetailsStore } from '@cases/stores/case-details'

/** Define emits. */
const emit = defineEmits([
  'addCaseCommentClick',
  'updateCaseCommentClick',
  'deleteCaseCommentClick',
  'editCaseStatusClick',
  'editCaseNotesClick',
  'editQueryPresetsClick',
  'editPedigreeClick',
  'updateCasePhenotypeTermsClick',
])

const Tabs = Object.freeze({
  overview: 'overview',
  qc: 'qc',
  annotation: 'annotation',
})

const currentTab = ref('overview')

const caseDetailsStore = useCaseDetailsStore()

const annosLoading = computed(
  () => caseDetailsStore.varAnnos === null || caseDetailsStore.svAnnos === null
)
const annoCount = computed(() => {
  if (annosLoading) {
    return null
  } else {
    return (
      caseDetailsStore.varAnnoList.length + caseDetailsStore.svAnnoList.length
    )
  }
})

/** Update the current tab. */
const updateCurrentTab = (newValue) => {
  currentTab.value = newValue
}

defineExpose({
  currentTab,
})
</script>

<template>
  <div
    :class="{
      'flex-grow-1 d-flex flex-column': currentTab === Tabs.annotation,
    }"
  >
    <ul class="nav nav-tabs" id="case-tab" role="tablist">
      <li class="nav-item">
        <a
          class="nav-link active"
          id="overview-tab"
          data-toggle="tab"
          href="#overview"
          role="tab"
          @click="updateCurrentTab(Tabs.overview)"
        >
          <i-mdi-account />
          Overview
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
      <li class="nav-item">
        <a
          class="nav-link"
          id="annotation-tab"
          data-toggle="tab"
          href="#annotation"
          role="tab"
          @click="updateCurrentTab(Tabs.annotation)"
        >
          <i-mdi-bookmark-multiple />

          Variant Annotation
          <span class="badge badge-pill badge-primary">
            <i-fa-solid-circle-notch v-if="annosLoading" class="spin" />
            <template v-if="!annosLoading">
              {{ annoCount }}
            </template>
          </span>
        </a>
      </li>
    </ul>
    <div class="tab-content flex-grow-1 d-flex flex-column" id="cases-content">
      <div
        v-if="currentTab === Tabs.overview"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        id="case-list"
        role="tabpanel"
      >
        <CaseDetailPaneCase
          @edit-case-status-click="emit('editCaseStatusClick')"
          @edit-case-notes-click="emit('editCaseNotesClick')"
          @edit-query-presets-click="emit('editQueryPresetsClick')"
          @add-case-comment-click="emit('addCaseCommentClick')"
          @update-case-comment-click="emit('updateCaseCommentClick', $event)"
          @delete-case-comment-click="emit('deleteCaseCommentClick', $event)"
          @edit-pedigree-click="emit('editPedigreeClick')"
          @update-case-phenotype-terms-click="
            emit('updateCasePhenotypeTermsClick', $event)
          "
        />
      </div>
      <div
        v-if="currentTab === Tabs.qc"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        id="case-list"
        role="tabpanel"
      >
        <CaseDetailPaneQc />
      </div>
      <div
        v-if="currentTab === Tabs.annotation"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        id="case-list"
        role="tabpanel"
      >
        <CaseDetailPaneAnnotations />
      </div>
    </div>
  </div>
</template>

<style scoped>
.spin {
  animation-name: spin;
  animation-duration: 2000ms;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
