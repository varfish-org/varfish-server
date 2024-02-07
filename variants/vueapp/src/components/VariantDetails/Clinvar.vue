<script setup lang="ts">
import { computed } from 'vue'

import { useVariantDetailsStore } from '@variants/stores/variantDetails'

const variantDetailsStore = useVariantDetailsStore()
const clinvar = computed(() => variantDetailsStore?.varAnnos?.clinvar)

const clinicalSignificanceLabel: { [key: string]: string } = {
  CLINICAL_SIGNIFICANCE_PATHOGENIC: 'pathogenic',
  CLINICAL_SIGNIFICANCE_LIKELY_PATHOGENIC: 'likely pathogenic',
  CLINICAL_SIGNIFICANCE_UNCERTAIN_SIGNIFICANCE: 'uncertain significance',
  CLINICAL_SIGNIFICANCE_LIKELY_BENIGN: 'likely benign',
  CLINICAL_SIGNIFICANCE_BENIGN: 'benign',
}

const reviewStatusLabel: { [key: string]: string } = {
  REVIEW_STATUS_PRACTICE_GUIDELINE: 'practice guideline',
  REVIEW_STATUS_REVIEWED_BY_EXPERT_PANEL: 'reviewed by expert panel',
  REVIEW_STATUS_CRITERIA_PROVIDED_MULTIPLE_SUBMITTERS_NO_CONFLICTS:
    'criteria provided, multiple submitters, no conflicts',
  REVIEW_STATUS_CRITERIA_PROVIDED_SINGLE_SUBMITTER:
    'criteria provided, single submitter',
  REVIEW_STATUS_CRITERIA_PROVIDED_CONFLICTING_INTERPRETATIONS:
    'criteria provided, conflicting interpretations',
  REVIEW_STATUS_NO_ASSERTION_CRITERIA_PROVIDED:
    'no assertion criteria provided',
  REVIEW_STATUS_NO_ASSERTION_PROVIDED: 'no assertion provided',
}

const reviewStatusStars: { [key: string]: number } = {
  REVIEW_STATUS_PRACTICE_GUIDELINE: 4,
  REVIEW_STATUS_REVIEWED_BY_EXPERT_PANEL: 3,
  REVIEW_STATUS_CRITERIA_PROVIDED_MULTIPLE_SUBMITTERS_NO_CONFLICTS: 2,
  REVIEW_STATUS_CRITERIA_PROVIDED_SINGLE_SUBMITTER: 2,
  REVIEW_STATUS_CRITERIA_PROVIDED_CONFLICTING_INTERPRETATIONS: 0,
  REVIEW_STATUS_NO_ASSERTION_CRITERIA_PROVIDED: 0,
  REVIEW_STATUS_NO_ASSERTION_PROVIDED: 0,
}

const genomePos = computed<string>(() => {
  if (!variantDetailsStore.smallVariant) {
    return ''
  } else {
    const { release, chromosome, start } = variantDetailsStore.smallVariant
    return `${release}:${chromosome}:${start}`
  }
})
</script>

<template>
  <div class="p-2">
    <a
      :href="`https://www.ncbi.nlm.nih.gov/clinvar/?term=${genomePos}`"
      target="_blank"
    >
      This location in ClinVar.
    </a>
  </div>
  <div class="p-2">
    <div class="text-muted small pb-2">
      <i-mdi-information />
      Note that VarFish is using a local copy of Clinvar to display this
      information. The link-outs to NCBI ClinVar will display the most current
      data that may differ from our "frozen" copy.
    </div>
    <div v-if="clinvar?.rcv">
      <div>
        <strong>Interpretation: </strong>
        {{ clinicalSignificanceLabel[clinvar.clinicalSignificance] }}
      </div>
      <div>
        <strong>Review Status: </strong>
        <template v-for="i of [1, 2, 3, 4, 5]">
          <i-mdi-star v-if="i <= reviewStatusStars[clinvar.reviewStatus]" />
          <i-mdi-star-outline v-else />
        </template>
        {{ reviewStatusLabel[clinvar.review_status] }}
      </div>
      <div>
        <strong>Accession: </strong>
        <a
          :href="`https://www.ncbi.nlm.nih.gov/clinvar/${clinvar.rcv}/`"
          target="_blank"
        >
          <i-mdi-launch />
          {{ clinvar.rcv }}
        </a>
      </div>
    </div>
    <div class="text-center text-muted font-italic" v-else>
      No ClinVar information available.
    </div>
  </div>
</template>
