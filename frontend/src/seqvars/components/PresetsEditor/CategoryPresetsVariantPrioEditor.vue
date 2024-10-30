<script setup lang="ts">
import { SeqvarsQueryPresetsVariantPrio } from '@varfish-org/varfish-api/lib'
import { debounce } from 'lodash'
import { computed, onMounted, ref, watch } from 'vue'
import { VForm } from 'vuetify/lib/components/index.mjs'

import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

import { CATEGORY_PRESETS_DEBOUNCE_WAIT } from './lib'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the current preset set version. */
    presetSetVersion?: string
    /** UUID of the query presets variant prio */
    variantPrioPresets?: string
    /** Whether the editor is readonly. */
    readonly: boolean
  }>(),
  { readonly: false },
)

/** This component's events. */
const emit = defineEmits<{
  /** Emit event to show a message. */
  message: [message: SnackbarMessage]
}>()

/** Store with the presets. */
const seqvarsPresetsStore = useSeqvarsPresetsStore()

/** The data that is to be edited by this component; component state. */
const data = ref<SeqvarsQueryPresetsVariantPrio | undefined>(undefined)

/** Shortcut to the number of variantPrio presets, used for rank. */
const maxRank = computed<number>(() => {
  if (props.presetSetVersion === undefined) {
    return 0
  }
  const presetSetVersion = seqvarsPresetsStore.presetSetVersions.get(
    props.presetSetVersion,
  )
  if (!presetSetVersion) {
    return 0
  }
  return presetSetVersion.seqvarsquerypresetsvariantprio_set.length
})

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Fill the data from the store. */
const fillData = () => {
  // Guard against missing preset set version or variantPrio.
  if (
    props.presetSetVersion === undefined ||
    props.variantPrioPresets === undefined
  ) {
    return
  }
  // Attempt to obtain the data from the store.
  const presetSetVersion = seqvarsPresetsStore.presetSetVersions.get(
    props.presetSetVersion,
  )
  if (!presetSetVersion) {
    emit('message', {
      text: 'Failed to find preset set version.',
      color: 'error',
    })
    return
  }
  const variantPrioPresets =
    presetSetVersion?.seqvarsquerypresetsvariantprio_set.find(
      (elem) => elem.sodar_uuid === props.variantPrioPresets,
    )
  if (!variantPrioPresets) {
    emit('message', {
      text: 'Failed to find variantPrio presets.',
      color: 'error',
    })
    return
  }

  data.value = { ...variantPrioPresets }
}

/**
 * Update the variantPrio presets in the store.
 *
 * Used directly when changing the rank (to minimize UI delay).
 *
 * @param rankDelta The delta to apply to the rank, if any.
 */
const updateVariantPrioPresets = async (rankDelta: number = 0) => {
  // Guard against missing/readonly/non-draft preset set version or missing variantPrio.
  if (
    props.variantPrioPresets === undefined ||
    props.presetSetVersion === undefined ||
    seqvarsPresetsStore.presetSetVersions.get(props.presetSetVersion)
      ?.status !== PresetSetVersionState.DRAFT ||
    data.value === undefined
  ) {
    return
  }

  // If necessary, update the rank of the other item as well via API and set
  // the new rank to `data.value.rank`.
  if (rankDelta !== 0) {
    const version = seqvarsPresetsStore.presetSetVersions.get(
      props.presetSetVersion,
    )
    if (
      version === undefined ||
      data.value.rank === undefined ||
      data.value.rank + rankDelta < 1 ||
      data.value.rank + rankDelta > maxRank.value
    ) {
      // Guard against invalid rank and version.
      return
    }
    // Find the next smaller or larger item, sort by rank.
    const others = version.seqvarsquerypresetsvariantprio_set.filter((elem) => {
      if (elem.sodar_uuid === props.variantPrioPresets) {
        return false
      }
      if (rankDelta < 0) {
        return (elem.rank ?? 0) < (data.value?.rank ?? 0)
      } else {
        return (elem.rank ?? 0) > (data.value?.rank ?? 0)
      }
    })
    others.sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
    // Then, pick the other item to flip ranks with.
    const other = others[rankDelta < 0 ? others.length - 1 : 0]
    // Store the other's rank in `data.value.rank` and update other via API.
    if (other) {
      const dataRank = data.value.rank
      data.value.rank = other.rank
      other.rank = dataRank
      try {
        await seqvarsPresetsStore.updateQueryPresetsVariantPrio(
          props.presetSetVersion,
          other,
        )
      } catch (error) {
        emit('message', {
          text: 'Failed to update variantPrio presets rank.',
          color: 'error',
        })
      }
    }
  }

  // Guard against invalid form data.
  const validateResult = await formRef.value?.validate()
  if (validateResult?.valid !== true) {
    return
  }
  try {
    await seqvarsPresetsStore.updateQueryPresetsVariantPrio(
      props.presetSetVersion,
      data.value,
    )
  } catch (error) {
    emit('message', {
      text: 'Failed to update variantPrio presets.',
      color: 'error',
    })
  }
}

/**
 * Update the variantPrio presets in the store -- debounced.
 *
 * Used for updating non-rank fields so that the UI does not lag.
 */
const updateVariantPrioPresetsDebounced = debounce(
  updateVariantPrioPresets,
  CATEGORY_PRESETS_DEBOUNCE_WAIT,
  { leading: true, trailing: true },
)

// Load data data from store when the UUID changes.
watch(
  () => props.variantPrioPresets,
  () => fillData(),
)
// Also, load data data from store when mounted.
onMounted(() => fillData())

// Watch the data and trigger a store update.
watch(data, () => updateVariantPrioPresetsDebounced(), { deep: true })
</script>

<template>
  <h4>
    Variant Priorization Presets &raquo;{{ data?.label ?? 'UNDEFINED' }}&laquo;
  </h4>

  <v-skeleton-loader v-if="!data" type="article" />
  <v-form v-else ref="formRef">
    <v-text-field
      v-model="data.label"
      :rules="[rules.required]"
      label="Label"
      clearable
      :disabled="readonly"
    />

    <div>
      <v-btn-group variant="outlined" divided>
        <v-btn
          prepend-icon="mdi-arrow-up-circle-outline"
          :disabled="
            props.readonly || data.rank === undefined || data.rank <= 1
          "
          @click="updateVariantPrioPresets(-1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly || data.rank === undefined || data.rank >= maxRank
          "
          @click="updateVariantPrioPresets(1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <v-sheet class="text-center font-italic bg-grey-lighten-3 pa-3 mt-3">
      Variant priorization presets editor is not implemented yet.
    </v-sheet>
    <div>
      Enabled:
      {{ data.variant_prio_enabled ? 'Yes' : 'No' }}
    </div>
    <div>
      Services/Algorithms:
      <span v-if="data?.services?.length === 0" class="text-grey-darken-2">
        N/A
      </span>
      <span v-else>
        <v-chip v-for="(service, index) in data.services ?? []" :key="index">
          {{ service.name }} ({{ service.version }})
        </v-chip>
      </span>
    </div>
  </v-form>
</template>
