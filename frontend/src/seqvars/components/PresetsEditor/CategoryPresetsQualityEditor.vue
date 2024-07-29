<script setup lang="ts">
import { SeqvarsQueryPresetsQuality } from '@varfish-org/varfish-api/lib'
import { PropType, watch } from 'vue'
import { debounce } from 'lodash'
import { CATEGORY_PRESETS_DEBOUNCE_WAIT } from './lib'
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether the editor is readonly. */
    readonly: boolean
  }>(),
  { readonly: false },
)

/** This component's events. */
const emit = defineEmits<{
  message: [message: SnackbarMessage]
}>()

/** The quality presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsQuality>,
})

// /** Store with the presets. */
// const seqvarsPresetsStore = useSeqvarsPresetsStore()

// /** Debounced version of the presets store's `updateQueryPresetsQuality` method. */
// const updateQueryPresetsQuality = debounce(
//   seqvarsPresetsStore.updateQueryPresetsQuality,
//   CATEGORY_PRESETS_DEBOUNCE_WAIT,
//   {leading: true}
// )

// // Watch the model deeply for changes and update the quality presets via the store
// // if the sodar_uuid changes.  The store will take care of updating the data on the
// // server and reactivity on its state takes care of UI state.
// watch(
//   () => model.value,
//   async (
//     newValue?: SeqvarsQueryPresetsQuality,
//     oldValue?: SeqvarsQueryPresetsQuality,
//   ) => {
//     if (
//       newValue?.sodar_uuid !== undefined &&
//       newValue?.sodar_uuid === oldValue?.sodar_uuid
//     ) {
//       try {
//         await updateQueryPresetsQuality(newValue.presetssetversion, newValue)
//       } catch (error) {
//         emit('message', {
//           text: `Failed to update quality presets: ${error}`,
//           color: 'error',
//         })
//       }
//     }
//   },
//   { deep: true },
// )
</script>

<template>
  <h4>Quality Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!model" type="article" />
  <v-form v-else>
    <v-checkbox
      v-model.number="model.filter_active"
      label="Filter Active"
      hide-details
      :disabled="readonly"
    />

    <div class="text-body-1 pb-3">
      Clear the fields below to remove the filter threshold.
    </div>

    <v-text-field
      v-model.number="model.min_dp_het"
      label="Min DP Het: minimal depth required for heterozygous genotypes."
      type="number"
      clearable
      :disabled="readonly"
    />

    <v-text-field
      v-model.number="model.min_dp_hom"
      label="Min DP Hom: minimal depth required for homozygous genotypes."
      type="number"
      clearable
      :disabled="readonly"
    />

    <v-text-field
      v-model.number="model.min_ab_het"
      label="Min AB Het: minimal allelic balance for heterozygous genotypes."
      type="number"
      step="0.01"
      clearable
      :disabled="readonly"
    />

    <v-text-field
      v-model.number="model.min_gq"
      label="Min GQ: minimal genotype quality required to pass."
      type="number"
      clearable
      :disabled="readonly"
    />

    <v-text-field
      v-model.number="model.min_ad"
      label="Min AD: minimal alternate read depth required to pass."
      type="number"
      clearable
      :disabled="readonly"
    />

    <v-text-field
      :value="model.max_ad"
      @input.integer="model.max_ad = $event.target.value ? parseInt($event.target.value) : null"
      label="Max AD: maximal alternate read depth allowed to pass."
      type="number"
      clearable
      :disabled="readonly"
    />
  </v-form>
</template>
