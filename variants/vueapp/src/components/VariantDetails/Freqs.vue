<script setup lang="ts">
import { isVariantMt } from '@varfish/moreUtils'

import VariantDetailsFreqsAutosomal from '@variants/components/VariantDetails/FreqsAutosomal.vue'
import VariantDetailsFreqsMitochondrial from '@variants/components/VariantDetails/FreqsMitochondrial.vue'

const props = defineProps<{
  smallVar: any
  varAnnos: any
}>()

const gnomadExomes = 'gnomad-exomes'
const gnomadGenomes = 'gnomad-genomes'
</script>

<template>
  <div>
    <VariantDetailsFreqsMitochondrial
      :small-var="props.smallVar"
      :var-annos="props.varAnnos"
      v-if="isVariantMt(props.smallVar)"
    />
    <div v-else>
      <VariantDetailsFreqsAutosomal
        :small-var="props.smallVar"
        :var-annos="props.varAnnos"
        :dataset="'gnomad-exomes'"
      />
      <VariantDetailsFreqsAutosomal
        :small-var="props.smallVar"
        :var-annos="props.varAnnos"
        :dataset="'gnomad-genomes'"
      />
    </div>
  </div>
</template>
