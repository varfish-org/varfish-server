<script setup lang="ts">
import { computed } from 'vue'

import { useVariantDetailsStore } from '@variants/stores/variantDetails'

const variantDetailsStore = useVariantDetailsStore()
const clinvar = computed(() => variantDetailsStore?.varAnnos?.clinvar)

const clinicalSignificanceLabel = [
  'pathogenic', // 0
  'likely pathogenic', // 1
  'uncertain signifiance', // 2
  'likely benign', // 3
  'benign', // 4
  'other',
]

const reviewStatusLabel = [
  'no assertion provided', // 0
  'no assertion criteria provided', // 1
  'criteria provided, conflicting interpretations', // 2
  'criteria provided, single submitter', // 3
  'criteria provided, multiple submitters, no conflicts', // 4
  'reviewed by expert panel', // 5
  'practice guideline', // 6
]

const reviewStatusStars = [0, 0, 0, 1, 2, 3, 4]
</script>

<template>
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
        {{ clinicalSignificanceLabel[clinvar.clinical_significance] }}
      </div>
      <div>
        <strong>Review Status: </strong>
        <template v-for="i of [1, 2, 3, 4, 5]">
          <i-mdi-star v-if="i <= reviewStatusStars[clinvar.review_status]" />
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
