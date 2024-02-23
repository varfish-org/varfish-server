<script setup>
import { computed } from 'vue'

import PaneCase from '@cases/components/CaseDetail/PaneCase.vue'
import PaneQc from '@cases_qc/components/PaneQc.vue'
import LegacyPaneQc from '@cases/components/CaseDetail/PaneQc.vue'
import PaneAnnotations from '@cases/components/CaseDetail/PaneAnnotations.vue'
import { useRouter } from 'vue-router'
import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import { useCaseQcStore } from '@cases_qc/stores/caseQc'

const router = useRouter()

const props = defineProps({
  /** The case UUID. */
  // eslint-disable-next-line vue/require-default-prop
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
})

const caseDetailsStore = useCaseDetailsStore()
const caseQcStore = useCaseQcStore()

const annosLoading = computed(
  () => caseDetailsStore.varAnnos === null || caseDetailsStore.svAnnos === null,
)
const annoCount = computed(() => {
  if (annosLoading.value) {
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
    <ul id="case-tab" class="nav nav-tabs" role="tablist">
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
    </ul>
    <div id="cases-content" class="tab-content flex-grow-1 d-flex flex-column">
      <div
        v-if="props.currentTab === Tabs.overview"
        id="case-list"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
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
        id="case-list"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        role="tabpanel"
      >
        <LegacyPaneQc v-if="caseDetailsStore.caseObj?.case_version !== 2" />
        <PaneQc v-else :stats="caseQcStore.varfishStats" />
      </div>
      <div
        v-if="props.currentTab === Tabs.annotation"
        id="case-list"
        class="border border-top-0 tab-pane fade show active flex-grow-1 d-flex flex-column"
        role="tabpanel"
      >
        <Suspense>
          <PaneAnnotations :case-uuid="props.caseUuid" />
          <template #fallback> Loading ... </template>
        </Suspense>
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
