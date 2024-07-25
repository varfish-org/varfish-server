<script setup lang="ts">
import { SeqvarsQueryPresetsPhenotypePrio } from '@varfish-org/varfish-api/lib'
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

/** The phenotype prio presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsPhenotypePrio>,
})
</script>

<template>
  <h4>
    Phenotype Prio Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;
  </h4>

  <v-skeleton-loader v-if="!model" type="article" />
  <v-form v-else>
    <v-sheet class="text-center font-italic bg-grey-lighten-3 pa-3 mt-3">
      Phenotype priorization presets editor is not implemented yet.
    </v-sheet>
    <div>
      Enabled:
      {{ model.phenotype_prio_enabled ? 'Yes' : 'No' }}
    </div>
    <div>
      Algorithm:
      {{ model.phenotype_prio_algorithm ?? 'N/A' }}
    </div>
    <div>
      Terms:
      <span v-if="model?.terms?.length === 0" class="text-grey-darken-2">
        N/A
      </span>
      <span v-else>
        <v-chip v-for="(term, index) in model.terms ?? []" :key="index">
          {{ term }}
        </v-chip>
      </span>
    </div>
  </v-form>
</template>
