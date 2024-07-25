<script setup lang="ts">
import { SeqvarsQueryPresetsClinvar } from '@varfish-org/varfish-api/lib'
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

/** The clinvar presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsClinvar>,
})

const labels = [
  'pathogenic',
  'likely_pathogenic',
  'uncertain_significance',
  'likely_benign',
  'benign',
]
</script>

<template>
  <h4>Clinvar Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!model" type="article" />
  <v-form v-else>
    <v-checkbox
      v-model="model.clinvar_presence_required"
      label="ClinVar presence required"
      hide-details
      density="compact"
      :disabled="readonly"
    />

    <div class="border-t-thin my-3"></div>

    <div>
      <v-checkbox
        v-for="label in labels"
        :key="label"
        v-model="model.clinvar_germline_aggregate_description"
        :label="label"
        :value="label"
        hide-details
        density="compact"
        :disabled="readonly"
      />
    </div>

    <div class="border-t-thin my-3"></div>

    <v-checkbox
      v-model="model.allow_conflicting_interpretations"
      label="Allow conflicting interpretations"
      hide-details
      density="compact"
      :disabled="readonly"
    />
  </v-form>
</template>
