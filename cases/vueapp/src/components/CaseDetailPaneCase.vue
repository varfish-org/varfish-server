<script setup>
import CaseDetailCardAlignmentQc from './CaseDetailCardAlignmentQc.vue'
import CaseDetailCardCaseAnnotations from './CaseDetailCardAnnotations.vue'
import CaseDetailCardCaseComments from './CaseDetailCardComments.vue'
import CaseDetailCardCase from './CaseDetailCardCase.vue'
import CaseDetailCardGeneAnnotations from './CaseDetailCardGeneAnnotations.vue'
import CaseDetailCardPedigree from './CaseDetailCardPedigree.vue'
import CaseDetailCardSvInfo from './CaseDetailCardSvInfo.vue'
import CaseDetailCardTerms from './CaseDetailCardTerms.vue'
import CaseDetailCardVariantQc from './CaseDetailCardVariantQc.vue'
import CaseDetailCardVariantsInfo from './CaseDetailCardVariantInfo.vue'
import CaseDetailCardQueries from './CaseDetailCardQueries.vue'

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
</script>

<template>
  <div class="position-relative mb-3">
    <div class="row pt-3">
      <div class="col-6">
        <CaseDetailCardCase
          @edit-case-status-click="emit('editCaseStatusClick')"
          @edit-case-notes-click="emit('editCaseNotesClick')"
        />
        <CaseDetailCardPedigree
          @edit-pedigree-click="emit('editPedigreeClick')"
        />
        <CaseDetailCardQueries
          @edit-query-presets-click="emit('editQueryPresetsClick')"
        />
        <CaseDetailCardVariantsInfo />
        <CaseDetailCardSvInfo />
      </div>
      <div class="col-6">
        <CaseDetailCardCaseComments
          @add-case-comment-click="emit('addCaseCommentClick')"
          @update-case-comment-click="emit('updateCaseCommentClick', $event)"
          @delete-case-comment-click="emit('deleteCaseCommentClick', $event)"
        />
        <CaseDetailCardTerms
          @update-case-phenotype-terms-click="
            emit('updateCasePhenotypeTermsClick', $event)
          "
        />
        <CaseDetailCardCaseAnnotations />
        <CaseDetailCardAlignmentQc />
        <CaseDetailCardVariantQc />
        <CaseDetailCardGeneAnnotations />
      </div>
    </div>
  </div>
</template>
