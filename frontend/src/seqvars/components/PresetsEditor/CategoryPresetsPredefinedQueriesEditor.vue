<script setup lang="ts">
import { SeqvarsPredefinedQuery } from '@varfish-org/varfish-api/lib'
import { PropType } from 'vue'

/** The predefined queries presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsPredefinedQuery>,
})
</script>

<template>
  <h4>
    Predefined Queries Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;
  </h4>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else> </v-form>
</template>
