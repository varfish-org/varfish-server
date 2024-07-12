<script setup lang="ts">
import { SeqvarsQueryPresetsQuality } from '@varfish-org/varfish-api/lib'
import { PropType } from 'vue';

/** The quality presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsQuality>,
})
</script>

<template>
  <h4> Quality </h4>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else>
    <v-checkbox v-model="model.filter_active" label="Filter Active" />
  </v-form>
</template>
