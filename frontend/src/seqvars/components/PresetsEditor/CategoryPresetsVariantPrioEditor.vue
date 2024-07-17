<script setup lang="ts">
import { SeqvarsQueryPresetsVariantPrio } from '@varfish-org/varfish-api/lib'
import { PropType } from 'vue'

/** The variant priorization presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsVariantPrio>,
})
</script>

<template>
  <h4>
    Variant Priorization Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;
  </h4>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else> </v-form>
</template>
