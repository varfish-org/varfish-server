<script setup>
import CaseDetailCardAlignmentQc from './CaseDetailCardAlignmentQc.vue'
import CaseDetailCardCaseAnnotations from './CaseDetailCardAnnotations.vue'
import CaseDetailCardCaseComments from './CaseDetailCardComments.vue'
import CaseDetailCardCaseDetails from './CaseDetailCardCase.vue'
import CaseDetailCardGeneAnnotations from './CaseDetailCardGeneAnnotations.vue'
import CaseDetailCardPedigree from './CaseDetailCardPedigree.vue'
import CaseDetailCardSvInfo from './CaseDetailCardSvInfo.vue'
import CaseDetailCardTerms from './CaseDetailCardTerms.vue'
import CaseDetailCardVariantQc from './CaseDetailCardVariantQc.vue'
import CaseDetailCardVariantsInfo from './CaseDetailCardVariantInfo.vue'
</script>

<template>
  <div class="position-relative mb-3">
    <div class="row pt-3">
      <div class="col-6">
        <CaseDetailCardCaseDetails />
        <CaseDetailCardPedigree />
        <CaseDetailCardVariantsInfo />
        <CaseDetailCardSvInfo />
      </div>
      <div class="col-6">
        <CaseDetailCardCaseComments />
        <CaseDetailCardTerms />
        <CaseDetailCardCaseAnnotations />
        <CaseDetailCardAlignmentQc />
        <CaseDetailCardVariantQc />
        <CaseDetailCardGeneAnnotations />
      </div>
    </div>
  </div>
</template>
