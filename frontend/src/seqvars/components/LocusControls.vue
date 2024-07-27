<script setup lang="ts">
import { Query } from '@/seqvars/types'

const model = defineModel<Query>({ required: true })
</script>

<template>
  <v-radio-group>
    <v-radio
      label="Gene list"
      :model-value="model.locus.genes"
      @update:model-value="
        (checked: boolean) => {
          if (checked) {
            model.locus.genes ||= []
            model.locus.gene_panels = undefined
          }
        }
      "
    ></v-radio>
    <v-radio
      label="Genomic regions"
      :model-value="model.locus.gene_panels"
      @update:model-value="
        (checked: boolean) => {
          if (checked) {
            model.locus.gene_panels ||= []
            model.locus.genes = undefined
          }
        }
      "
    ></v-radio>
  </v-radio-group>
</template>
