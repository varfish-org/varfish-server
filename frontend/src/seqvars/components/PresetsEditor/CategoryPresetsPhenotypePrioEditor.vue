<script setup lang="ts">
import { SeqvarsQueryPresetsPhenotypePrio } from '@varfish-org/varfish-api/lib'
import { PropType } from 'vue'

/** The phenotype prio presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsPhenotypePrio>,
})
</script>

<template>
  <h4>
    Phenotype Prio Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;
  </h4>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else> </v-form>
</template>
