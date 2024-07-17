<script setup lang="ts">
import { SeqvarsQueryPresetsClinvar } from '@varfish-org/varfish-api/lib'
import { PropType } from 'vue'

/** The clinvar presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsClinvar>,
})
</script>

<template>
  <h4>Clinvar Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else> </v-form>
</template>
