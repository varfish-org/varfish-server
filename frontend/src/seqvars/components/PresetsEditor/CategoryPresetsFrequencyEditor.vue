<script setup lang="ts">
import { SeqvarsQueryPresetsFrequency } from '@varfish-org/varfish-api/lib'
import { computed, onMounted, ref, watch } from 'vue'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'
import { GnomadFreqs, MitochondrialFreqs, InhouseFreqs } from './types'
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets';
import { VForm } from 'vuetify/lib/components/index.mjs';
import { PresetSetVersionState } from '@/seqvars/stores/presets/types';
import debounce from 'lodash.debounce';
import { CATEGORY_PRESETS_DEBOUNCE_WAIT } from './lib';

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the current preset set version. */
    presetSetVersion?: string
    /** UUID of the query presets frequency */
    frequencyPresets?: string
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
const data = ref<SeqvarsQueryPresetsFrequency | undefined>(undefined)

/** Shortcut to the number of frequency presets, used for rank. */
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
  return presetSetVersion.seqvarsquerypresetsfrequency_set.length
})

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Fill the data from the store. */
const fillData = () => {
  // Guard against missing preset set version or frequency.
  if (
    props.presetSetVersion === undefined ||
    props.frequencyPresets === undefined
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
  const frequencyPresets = presetSetVersion?.seqvarsquerypresetsfrequency_set.find(
    (elem) => elem.sodar_uuid === props.frequencyPresets,
  )
  if (!frequencyPresets) {
    emit('message', {
      text: 'Failed to find frequency presets.',
      color: 'error',
    })
    return
  }

  data.value = { ...frequencyPresets }
}

/** Helper for guarding against undefined `data.value` for `gnomadExomes`. */
const gnomadExomes = computed<GnomadFreqs>(
  () => data.value?.gnomad_exomes ?? ({} as GnomadFreqs),
)
/** Helper for guarding against undefined `data.value` for `gnomadGenomes`. */
const gnomadGenomes = computed<GnomadFreqs>(
  () => data.value?.gnomad_genomes ?? ({} as GnomadFreqs),
)
/** Helper for guarding against undefined `data.value` for `gnomadMitochondrial`. */
const gnomadMitochondrial = computed<MitochondrialFreqs>(
  () => data.value?.gnomad_mitochondrial ?? ({} as MitochondrialFreqs),
)
/** Helper for guarding against undefined `data.value` for `helixMtDb`. */
const helixMtDb = computed<MitochondrialFreqs>(
  () => data.value?.helixmtdb ?? ({} as MitochondrialFreqs),
)
/** Helper for guarding against undefined `data.value` for `inhouse`. */
const inhouse = computed<InhouseFreqs>(
  () => data.value?.inhouse ?? ({} as InhouseFreqs),
)

/**
 * Update the frequency presets in the store.
 *
 * Used directly when changing the rank (to minimize UI delay).
 *
 * @param rankDelta The delta to apply to the rank, if any.
 */
 const updateFrequencyPresets = async (rankDelta: number = 0) => {
  // Guard against missing/readonly/non-draft preset set version or missing frequency.
  if (
    props.frequencyPresets === undefined ||
    props.presetSetVersion === undefined ||
    seqvarsPresetsStore.factoryDefaultPresetSetUuids.includes(
      props.frequencyPresets,
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
    const others = version.seqvarsquerypresetsfrequency_set.filter((elem) => {
      if (elem.sodar_uuid === props.frequencyPresets) {
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
        await seqvarsPresetsStore.updateQueryPresetsFrequency(
          props.presetSetVersion,
          other,
        )
      } catch (error) {
        emit('message', {
          text: 'Failed to update frequency presets rank.',
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
    await seqvarsPresetsStore.updateQueryPresetsFrequency(
      props.presetSetVersion,
      data.value,
    )
  } catch (error) {
    emit('message', {
      text: 'Failed to update frequency presets.',
      color: 'error',
    })
  }
}

/**
 * Update the frequency presets in the store -- debounced.
 *
 * Used for updating non-rank fields so that the UI does not lag.
 */
const updateFrequencyPresetsDebounced = debounce(
  updateFrequencyPresets,
  CATEGORY_PRESETS_DEBOUNCE_WAIT,
  { leading: true, trailing: true },
)

// Load model data from store when the UUID changes.
watch(
  () => props.frequencyPresets,
  () => fillData(),
)
// Also, load model data from store when mounted.
onMounted(() => fillData())

// Watch the data and trigger a store update.
watch(data, () => updateFrequencyPresetsDebounced(), { deep: true })
</script>

<template>
  <h4>Frequency Presets &raquo;{{ data?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!data" type="article" />
  <v-form v-else>
    <v-table density="compact">
      <thead>
        <tr>
          <th class="px-1 text-center">database</th>
          <th class="px-1 text-center">enabled</th>
          <th class="px-1 text-center">hom.</th>
          <th class="px-1 text-center">het.</th>
          <th class="px-1 text-center">hemi.</th>
          <th class="px-1 text-center">freq. [%]</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th class="px-1">gnomAD exomes</th>
          <td class="px-1">
            <v-checkbox
              v-model="gnomadExomes.enabled"
              hide-details
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadExomes.homozygous"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadExomes.heterozygous"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadExomes.hemizygous"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadExomes.frequency"
              hide-details
              density="compact"
              clearable
              type="number"
              step="0.001"
              :disabled="readonly"
            />
          </td>
        </tr>
        <tr>
          <th class="px-1">gnomAD genomes</th>
          <td class="px-1">
            <v-checkbox
              v-model="gnomadGenomes.enabled"
              hide-details
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadGenomes.homozygous"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadGenomes.heterozygous"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadGenomes.hemizygous"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadGenomes.frequency"
              hide-details
              density="compact"
              clearable
              type="number"
              step="0.001"
              :disabled="readonly"
            />
          </td>
        </tr>
        <tr>
          <th class="px-1">gnomAD MT</th>
          <td class="px-1">
            <v-checkbox
              v-model="gnomadMitochondrial.enabled"
              hide-details
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadMitochondrial.homoplasmic"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadMitochondrial.heteroplasmic"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1 text-center text-grey">N/A</td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadMitochondrial.frequency"
              hide-details
              density="compact"
              clearable
              type="number"
              step="0.001"
              :disabled="readonly"
            />
          </td>
        </tr>
        <tr>
          <th class="px-1">HelixMtDb</th>
          <td class="px-1">
            <v-checkbox
              v-model="helixMtDb.enabled"
              hide-details
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="helixMtDb.homoplasmic"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="helixMtDb.heteroplasmic"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1 text-center text-grey">N/A</td>
          <td class="px-1">
            <v-text-field
              v-model="helixMtDb.frequency"
              hide-details
              density="compact"
              clearable
              type="number"
              step="0.001"
              :disabled="readonly"
            />
          </td>
        </tr>
        <tr>
          <th class="px-1 text-center">database</th>
          <th class="px-1 text-center">enabled</th>
          <th class="px-1 text-center">hom.</th>
          <th class="px-1 text-center">het.</th>
          <th class="px-1 text-center">hemi.</th>
          <th class="px-1 text-center"># carriers</th>
        </tr>
        <tr>
          <th class="px-1">In-House</th>
          <td class="px-1">
            <v-checkbox
              v-model="inhouse.enabled"
              hide-detail
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="inhouse.homozygous"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="inhouse.heterozygous"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="inhouse.hemizygous"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="inhouse.carriers"
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
            />
          </td>
        </tr>
      </tbody>
    </v-table>
  </v-form>
</template>
