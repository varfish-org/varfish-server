<script setup>
import { computed, ref } from 'vue'

import PaneCase from '@cases/components/CaseDetail/PaneCase.vue'
import PaneQc from '@cases_qc/components/PaneQc.vue'
import LegacyPaneQc from '@cases/components/CaseDetail/PaneQc.vue'
import PaneAnnotations from '@cases/components/CaseDetail/PaneAnnotations.vue'
import { useRouter } from 'vue-router'
import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import GenomeBrowser from '@svs/components/GenomeBrowser.vue'

const router = useRouter()

const props = defineProps({
  /** The case UUID. */
  caseUuid: String,
  currentTab: {
    type: String,
    default: 'overview', // keep in sync with Tabs.caseList
  },
})

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
  browser: 'browser',
})

const caseDetailsStore = useCaseDetailsStore()

const annosLoading = computed(
  () => caseDetailsStore.varAnnos === null || caseDetailsStore.svAnnos === null,
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
  router.push({
    name: 'case-detail-' + newValue,
    params: { case: caseDetailsStore.caseObj.sodar_uuid },
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
          :class="{ active: props.currentTab === Tabs.overview }"
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
          :class="{ active: props.currentTab === Tabs.qc }"
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
          :class="{ active: props.currentTab === Tabs.annotation }"
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
          :class="{ active: props.currentTab === Tabs.browser }"
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
        v-if="props.currentTab === Tabs.overview"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        id="case-list"
        role="tabpanel"
      >
        <PaneCase
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
        v-if="props.currentTab === Tabs.qc && caseDetailsStore.caseObj"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        id="case-list"
        role="tabpanel"
      >
        <LegacyPaneQc v-if="caseDetailsStore.caseObj?.case_version !== 2" />
        <PaneQc v-else />
      </div>
      <div
        v-if="props.currentTab === Tabs.annotation"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        id="case-list"
        role="tabpanel"
      >
        <Suspense>
          <PaneAnnotations :case-uuid="props.caseUuid" />
          <template #fallback> Loading ... </template>
        </Suspense>
      </div>
      <div
        v-if="props.currentTab === Tabs.browser"
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
