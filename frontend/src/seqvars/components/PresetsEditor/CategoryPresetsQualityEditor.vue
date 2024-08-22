<script setup lang="ts">
import { SeqvarsQueryPresetsQuality } from '@varfish-org/varfish-api/lib'
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
    /** UUID of the query presets quality */
    qualityPresets?: string
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
const data = ref<SeqvarsQueryPresetsQuality | undefined>(undefined)

/** Shortcut to the number of quality presets, used for rank. */
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
  return presetSetVersion.seqvarsquerypresetsquality_set.length
})

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Fill the data from the store. */
const fillData = () => {
  // Guard against missing preset set version or quality.
  if (
    props.presetSetVersion === undefined ||
    props.qualityPresets === undefined
  ) {
    return
  }
  // Attempt to obtain the model from the store.
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
  const qualityPresets = presetSetVersion?.seqvarsquerypresetsquality_set.find(
    (elem) => elem.sodar_uuid === props.qualityPresets,
  )
  if (!qualityPresets) {
    emit('message', {
      text: 'Failed to find quality presets.',
      color: 'error',
    })
    return
  }

  data.value = { ...qualityPresets }
}

/**
 * Update the quality presets in the store.
 *
 * Used directly when changing the rank (to minimize UI delay).
 *
 * @param rankDelta The delta to apply to the rank, if any.
 */
const updateQualityPresets = async (rankDelta: number = 0) => {
  // Guard against missing/readonly/non-draft preset set version or missing quality.
  if (
    props.qualityPresets === undefined ||
    props.presetSetVersion === undefined ||
    seqvarsPresetsStore.factoryDefaultPresetSetUuids.includes(
      props.qualityPresets,
    ) ||
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
    const others = version.seqvarsquerypresetsquality_set.filter((elem) => {
      if (elem.sodar_uuid === props.qualityPresets) {
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
        await seqvarsPresetsStore.updateQueryPresetsQuality(
          props.presetSetVersion,
          other,
        )
      } catch (error) {
        emit('message', {
          text: 'Failed to update quality presets rank.',
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
    await seqvarsPresetsStore.updateQueryPresetsQuality(
      props.presetSetVersion,
      data.value,
    )
  } catch (error) {
    emit('message', {
      text: 'Failed to update quality presets.',
      color: 'error',
    })
  }
}

/**
 * Update the quality presets in the store -- debounced.
 *
 * Used for updating non-rank fields so that the UI does not lag.
 */
const updateQualityPresetsDebounced = debounce(
  updateQualityPresets,
  CATEGORY_PRESETS_DEBOUNCE_WAIT,
  { leading: true, trailing: true },
)

// Load model data from store when the UUID changes.
watch(
  () => props.qualityPresets,
  () => fillData(),
)
// Also, load model data from store when mounted.
onMounted(() => fillData())

// Watch the data and trigger a store update.
watch(data, () => updateQualityPresetsDebounced(), { deep: true })
</script>

<template>
  <h4>Quality Presets &raquo;{{ data?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!data" type="article" />
  <v-form v-else ref="formRef">
    <v-checkbox
      v-model="data.filter_active"
      label="Filter Active"
      hide-details
      :disabled="readonly"
    />

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
          @click="updateQualityPresets(-1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly || data.rank === undefined || data.rank >= maxRank
          "
          @click="updateQualityPresets(1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <div class="text-body-1 pb-3 pt-3">
      Clear the fields below to remove the filter threshold.
    </div>

    <v-number-input
      v-model="data.min_dp_het"
      label="Min DP Het: minimal depth required for heterozygous genotypes."
      clearable
      control-variant="stacked"
      :disabled="readonly"
    />

    <v-number-input
      v-model="data.min_dp_hom"
      label="Min DP Hom: minimal depth required for homozygous genotypes."
      clearable
      control-variant="stacked"
      :disabled="readonly"
    />

    <v-number-input
      v-model="data.min_ab_het"
      label="Min AB Het: minimal allelic balance for heterozygous genotypes."
      :step="0.01"
      clearable
      control-variant="stacked"
      :disabled="readonly"
    />

    <v-number-input
      v-model="data.min_gq"
      label="Min GQ: minimal genotype quality required to pass."
      clearable
      control-variant="stacked"
      :disabled="readonly"
    />

    <v-number-input
      v-model="data.min_ad"
      label="Min AD: minimal alternate read depth required to pass."
      clearable
      control-variant="stacked"
      :disabled="readonly"
    />

    <v-number-input
      v-model="data.max_ad"
      label="Max AD: maximal alternate read depth allowed to pass."
      clearable
      control-variant="stacked"
      :disabled="readonly"
    />
  </v-form>
</template>
