<script setup lang="ts">
import { SeqvarsQueryPresetsLocus } from '@varfish-org/varfish-api/lib'
import { PropType } from 'vue'

/** The locus presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsLocus>,
})
</script>

<template>
  <h4>Locus Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else> </v-form>
</template>
