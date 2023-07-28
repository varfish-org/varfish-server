<script setup>
import { computed, ref } from 'vue'

import CaseDetailPaneCase from './CaseDetailPaneCase.vue'
import CaseDetailPaneQc from './CaseDetailPaneQc.vue'
import CaseDetailPaneAnnotations from './CaseDetailPaneAnnotations.vue'
import { useCaseDetailsStore } from '@cases/stores/case-details.js'
import GenomeBrowser from '@svs/components/GenomeBrowser.vue'
import { useRouter } from 'vue-router'

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

const props = defineProps({
  /** Whether to show the variant details modal. */
  variantDetailsModalVisible: Boolean,
  /** The UUID of the result row to show in details modal. */
  variantDetailsModalResultRowUuid: String,
  /** Which tab to show in the variant details modal. */
  variantDetailsModalSelectedTab: String,
  /** The currently selected tab. */
  caseDetailsSelectedTab: String,
})

const Tabs = Object.freeze({
  overview: 'overview',
  qc: 'qc',
  annotation: 'annotation',
  browser: 'browser',
})

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
  <div
    :class="{
      'flex-grow-1 d-flex flex-column': props.currentTab === Tabs.annotation,
    }"
  >
    <ul class="nav nav-tabs" id="case-tab" role="tablist">
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: props.caseDetailsSelectedTab === Tabs.overview }"
          role="button"
          @click="updateCurrentTab(Tabs.overview)"
        >
          <i-mdi-account />
          Overview
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: props.caseDetailsSelectedTab === Tabs.qc }"
          role="button"
          @click="updateCurrentTab(Tabs.qc)"
        >
          <i-mdi-chart-multiple />
          Quality Control
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: props.caseDetailsSelectedTab === Tabs.annotation }"
          role="button"
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
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: props.caseDetailsSelectedTab === Tabs.browser }"
          role="button"
          @click="updateCurrentTab(Tabs.browser)"
        >
          <i-mdi-safety-goggles />

          Browser
        </a>
      </li>
    </ul>
    <div class="tab-content flex-grow-1 d-flex flex-column" id="cases-content">
      <div
        v-if="props.caseDetailsSelectedTab === Tabs.overview"
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
        v-if="props.caseDetailsSelectedTab === Tabs.qc"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        id="case-list"
        role="tabpanel"
      >
        <CaseDetailPaneQc />
      </div>
      <div
        v-if="props.caseDetailsSelectedTab === Tabs.annotation"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        id="case-list"
        role="tabpanel"
      >
        <CaseDetailPaneAnnotations
          :detailsModalVisible="props.detailsModalVisible"
          :detailsModalResultRowUuid="props.detailsModalResultRowUuid"
          :detailsModalSelectedTab="props.detailsModalSelectedTab"
        />
      </div>
      <div
        v-if="props.caseDetailsSelectedTab === Tabs.browser"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        id="case-list"
        role="tabpanel"
      >
        <GenomeBrowser
          :case-uuid="caseDetailsStore.caseObj?.sodar_uuid"
          :genome="caseDetailsStore.caseObj?.release"
        />
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
