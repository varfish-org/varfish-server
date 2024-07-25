<script setup lang="ts">
import { SeqvarsQueryPresetsColumns } from '@varfish-org/varfish-api/lib'
import { PropType } from 'vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether the editor is readonly. */
    readonly: boolean
  }>(),
  { readonly: false },
)

/** The columns presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsColumns>,
})
</script>

<template>
  <h4>Columns Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!model" type="article" />
  <v-form v-else>
    <v-sheet class="text-center font-italic bg-grey-lighten-3 pa-3 mt-3">
      Columns presets editor is not implemented yet.
    </v-sheet>
  </v-form>
</template>
