<script setup lang="ts">
import { SeqvarsQueryPresetsVariantPrio } from '@varfish-org/varfish-api/lib'
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

/** The variant priorization presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsVariantPrio>,
})
</script>

<template>
  <h4>
    Variant Priorization Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;
  </h4>

  <v-skeleton-loader v-if="!model" type="article" />
  <v-form v-else>
    <v-sheet class="text-center font-italic bg-grey-lighten-3 pa-3 mt-3">
      Variant priorization presets editor is not implemented yet.
    </v-sheet>
    <div>
      Enabled:
      {{ model.variant_prio_enabled ? 'Yes' : 'No' }}
    </div>
    <div>
      Services/Algorithms:
      <span v-if="model?.services?.length === 0" class="text-grey-darken-2">
        N/A
      </span>
      <span v-else>
        <v-chip v-for="(service, index) in model.services ?? []" :key="index">
          {{ service.name }} ({{ service.version }})
        </v-chip>
      </span>
    </div>
  </v-form>
</template>
