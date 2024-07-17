<script setup lang="ts">
import { SeqvarsQueryPresetsColumns } from '@varfish-org/varfish-api/lib'
import { PropType } from 'vue'

/** The columns presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsColumns>,
})
</script>

<template>
  <h4>Columns Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else> </v-form>
</template>
