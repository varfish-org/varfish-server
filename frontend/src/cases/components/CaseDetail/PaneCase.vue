<script setup>
import CaseDetailCardAlignmentQc from '@/cases/components/CaseDetail/CardAlignmentQc.vue'
import CaseDetailCardCaseAnnotations from '@/cases/components/CaseDetail/CardAnnotations.vue'
import CaseDetailCardCase from '@/cases/components/CaseDetail/CardCase.vue'
import CaseDetailCardCaseComments from '@/cases/components/CaseDetail/CardComments.vue'
import CaseDetailCardGeneAnnotations from '@/cases/components/CaseDetail/CardGeneAnnotations.vue'
import CaseDetailCardPedigree from '@/cases/components/CaseDetail/CardPedigree.vue'
import CaseDetailCardQueries from '@/cases/components/CaseDetail/CardQueries.vue'
import CaseDetailCardSvInfo from '@/cases/components/CaseDetail/CardSvInfo.vue'
import CaseDetailCardTerms from '@/cases/components/CaseDetail/CardTerms.vue'
import CaseDetailCardVariantsInfo from '@/cases/components/CaseDetail/CardVariantInfo.vue'
import CaseDetailCardVariantQc from '@/cases/components/CaseDetail/CardVariantQc.vue'

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

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
