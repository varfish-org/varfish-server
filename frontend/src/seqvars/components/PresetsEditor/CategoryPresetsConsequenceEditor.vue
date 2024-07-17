<script setup lang="ts">
import { SeqvarsQueryPresetsConsequence } from '@varfish-org/varfish-api/lib'
import { PropType } from 'vue'

/** The consequence presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsConsequence>,
})
</script>

<template>
  <h4>Consequence Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else> </v-form>
</template>
