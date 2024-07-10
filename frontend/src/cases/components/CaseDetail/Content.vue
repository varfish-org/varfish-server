<script setup>
import PaneCase from '@/cases/components/CaseDetail/PaneCase.vue'
import PaneQc from '@/cases_qc/components/PaneQc.vue'
import LegacyPaneQc from '@/cases/components/CaseDetail/PaneQc.vue'
import PaneAnnotations from '@/cases/components/CaseDetail/PaneAnnotations.vue'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { useCaseQcStore } from '@/cases_qc/stores/caseQc'

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
</script>

<template>
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
      <PaneAnnotations />
      <template #fallback> Loading ... </template>
    </Suspense>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
