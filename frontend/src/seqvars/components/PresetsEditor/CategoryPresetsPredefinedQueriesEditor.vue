<script setup lang="ts">
import { SeqvarsPredefinedQuery } from '@varfish-org/varfish-api/lib'
import { GENOTYPE_PRESET_LABELS } from './lib'
import { ref, onMounted, watch, computed } from 'vue'
import { debounce } from 'lodash'
import { CATEGORY_PRESETS_DEBOUNCE_WAIT } from './lib'
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'
import { VForm } from 'vuetify/lib/components/index.mjs'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** Preset set version to take presets from. */
    presetSetVersion?: string
    /** UUID of the query presets predefined queries */
    predefinedQueriesPresets?: string
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
const data = ref<SeqvarsPredefinedQuery | undefined>(undefined)

/** Shortcut to the presets set version from props. */
const presetSetVersionObj = computed(() => {
  return seqvarsPresetsStore.presetSetVersions.get(props.presetSetVersion ?? '')
})

/** Shortcut to the number of predefinedQueries presets, used for rank. */
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
  return presetSetVersionObj.value?.seqvarspredefinedquery_set.length ?? 0
})

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Fill the data from the store. */
const fillData = () => {
  // Guard against missing preset set version or predefinedQueries.
  if (
    props.presetSetVersion === undefined ||
    props.predefinedQueriesPresets === undefined
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
  const predefinedQueriesPresets =
    presetSetVersion?.seqvarspredefinedquery_set.find(
      (elem) => elem.sodar_uuid === props.predefinedQueriesPresets,
    )
  if (!predefinedQueriesPresets) {
    emit('message', {
      text: 'Failed to find predefinedQueries presets.',
      color: 'error',
    })
    return
  }

  data.value = { ...predefinedQueriesPresets }
}

/**
 * Update the predefinedQueries presets in the store.
 *
 * Used directly when changing the rank (to minimize UI delay).
 *
 * @param rankDelta The delta to apply to the rank, if any.
 */
const updatePredefinedQueriesPresets = async (rankDelta: number = 0) => {
  // Guard against missing/readonly/non-draft preset set version or missing predefinedQueries.
  if (
    props.predefinedQueriesPresets === undefined ||
    props.presetSetVersion === undefined ||
    seqvarsPresetsStore.factoryDefaultPresetSetUuids.includes(
      props.predefinedQueriesPresets,
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
    const others = version.seqvarspredefinedquery_set.filter((elem) => {
      if (elem.sodar_uuid === props.predefinedQueriesPresets) {
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
        await seqvarsPresetsStore.updateQueryPresetsPredefinedQuery(
          props.presetSetVersion,
          other,
        )
      } catch (error) {
        emit('message', {
          text: 'Failed to update predefinedQueries presets rank.',
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
    await seqvarsPresetsStore.updateQueryPresetsPredefinedQuery(
      props.presetSetVersion,
      data.value,
    )
  } catch (error) {
    emit('message', {
      text: 'Failed to update predefinedQueries presets.',
      color: 'error',
    })
  }
}

/**
 * Update the predefinedQueries presets in the store -- debounced.
 *
 * Used for updating non-rank fields so that the UI does not lag.
 */
const updatePredefinedQueriesPresetsDebounced = debounce(
  updatePredefinedQueriesPresets,
  CATEGORY_PRESETS_DEBOUNCE_WAIT,
  { leading: true, trailing: true },
)

/**
 * Helper that extracts items for the dropdowns.
 */
const extractItems = (
  rawItems: { sodar_uuid: string; label: string }[],
): { value: string; title: string }[] =>
  rawItems.map((elem) => ({
    value: elem.sodar_uuid,
    title: elem.label,
  }))

// Load data data from store when the UUID changes.
watch(
  () => props.predefinedQueriesPresets,
  () => fillData(),
)
// Also, load data data from store when mounted.
onMounted(() => fillData())

// Watch the data and trigger a store update.
watch(data, () => updatePredefinedQueriesPresetsDebounced(), { deep: true })
</script>

<template>
  <h4>
    Predefined Queries Presets &raquo;{{ data?.label ?? 'UNDEFINED' }}&laquo;
  </h4>

  <v-skeleton-loader v-if="!data || !presetSetVersionObj" type="article" />
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
          @click="updatePredefinedQueriesPresets(-1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly || data.rank === undefined || data.rank >= maxRank
          "
          @click="updatePredefinedQueriesPresets(1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <div class="border-t-thin my-3"></div>

    <v-checkbox
      v-model="data.included_in_sop"
      label="Include in SOP"
      hint="The queries that are included in SOP can be auto-started together."
      density="compact"
      persistent-hint
      :disabled="readonly"
    />

    <div class="border-t-thin my-3"></div>

    <v-select
      v-model="data.genotype!.choice"
      label="Genotype Preset"
      :items="Object.keys(GENOTYPE_PRESET_LABELS)"
      :item-title="
        (key: keyof typeof GENOTYPE_PRESET_LABELS) =>
          GENOTYPE_PRESET_LABELS[key]
      "
      :disabled="readonly"
    />

    <v-select
      v-model="data.quality"
      label="Quality Preset"
      :items="extractItems(presetSetVersionObj!.seqvarsquerypresetsquality_set)"
      item-props
      :disabled="readonly"
    />

    <v-select
      v-model="data.frequency"
      label="Frequency Preset"
      :items="
        extractItems(presetSetVersionObj!.seqvarsquerypresetsfrequency_set)
      "
      item-props
      :disabled="readonly"
    />

    <v-select
      v-model="data.consequence"
      label="Consequence Preset"
      :items="
        extractItems(presetSetVersionObj!.seqvarsquerypresetsconsequence_set)
      "
      item-props
      :disabled="readonly"
    />

    <v-select
      v-model="data.locus"
      label="Locus Preset"
      :items="extractItems(presetSetVersionObj!.seqvarsquerypresetslocus_set)"
      item-props
      :disabled="readonly"
    />

    <v-select
      v-model="data.phenotypeprio"
      label="Phenotype Priority Preset"
      :items="
        extractItems(presetSetVersionObj!.seqvarsquerypresetsphenotypeprio_set)
      "
      item-props
      :disabled="readonly"
    />

    <v-select
      v-model="data.variantprio"
      label="Variant Priority Preset"
      :items="
        extractItems(presetSetVersionObj!.seqvarsquerypresetsvariantprio_set)
      "
      item-props
      :disabled="readonly"
    />

    <v-select
      v-model="data.clinvar"
      label="Clinvar Preset"
      :items="extractItems(presetSetVersionObj!.seqvarsquerypresetsclinvar_set)"
      item-props
      :disabled="readonly"
    />

    <v-select
      v-model="data.columns"
      label="Columns Preset"
      :items="extractItems(presetSetVersionObj!.seqvarsquerypresetscolumns_set)"
      item-props
      :disabled="readonly"
    />
  </v-form>
</template>
