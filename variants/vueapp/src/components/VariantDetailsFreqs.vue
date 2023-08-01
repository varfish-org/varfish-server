<script setup lang="ts">
import { isVariantMt } from '@varfish/more-utils'

import VariantDetailsFreqsAutosomal from '@variants/components/VariantDetailsFreqsAutosomal.vue'
import VariantDetailsFreqsMitochondrial from '@variants/components/VariantDetailsFreqsMitochondrial.vue'

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
