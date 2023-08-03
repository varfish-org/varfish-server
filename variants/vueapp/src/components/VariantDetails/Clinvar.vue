<script setup lang="ts">
import { computed } from 'vue'

import { useVariantDetailsStore } from '@variants/stores/variantDetails'

const variantDetailsStore = useVariantDetailsStore()
const clinvar = computed(() => variantDetailsStore?.varAnnos?.clinvar)

const interpretations = [
  'N/A',
  'Benign',
  'Likely benign',
  'Uncertain signifiance',
  'Likely pathogenic',
  'Pathogenic',
]

const reviewStatus = (goldStars: number): string => {
  const res = []
  for (let i = 1; i <= 5; i++) {
    res.push()
  }
  return res.join('')
}
</script>

<template>
  <div class="p-2">
    <div class="text-muted small pb-2">
      <i-mdi-information />
      Note that VarFish is using a local copy of Clinvar to display this
      information. The link-outs to NCBI ClinVar will display the most current
      data that may differ from our "frozen" copy.
    </div>
    <div v-if="clinvar?.vcv">
      <div>
        <strong>Interpretation: </strong>
        {{
          clinvar.summary_clinvar_pathogenicity
            .map((num) => interpretations[num])
            .join(', ')
        }}
      </div>
      <div>
        <strong>Review Status: </strong>
        <template v-for="i of [1, 2, 3, 4, 5]">
          <i-mdi-star v-if="i <= clinvar.summary_clinvar_gold_stars" />
          <i-mdi-star-outline v-else />
        </template>
      </div>
      <div>
        <strong>Accession: </strong>
        <a
          :href="`https://www.ncbi.nlm.nih.gov/clinvar/?term=${clinvar.vcv}`"
          target="_blank"
        >
          <i-mdi-launch />
          {{ clinvar.vcv }}
        </a>
      </div>
    </div>
    <div class="text-center text-muted font-italic" v-else>
      No ClinVar information available.
    </div>
  </div>
</template>
