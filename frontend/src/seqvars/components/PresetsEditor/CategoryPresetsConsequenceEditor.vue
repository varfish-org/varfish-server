<script setup lang="ts">
import { SeqvarsQueryPresetsConsequence } from '@varfish-org/varfish-api/lib'
import { debounce } from 'lodash'
import { computed, onMounted, ref, watch } from 'vue'
import { VForm } from 'vuetify/lib/components/index.mjs'

import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

import {
  CATEGORY_PRESETS_DEBOUNCE_WAIT,
  CODING_CONSEQUENCES,
  CONSEQUENCE_GROUP_INFOS,
  ConsequenceGroup,
  ConsequenceGroupState,
  NON_CODING_CONSEQUENCES,
  OFF_EXOMES_CONSEQUENCES,
  SPLICING_CONSEQUENCES,
} from './lib'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the current preset set version. */
    presetSetVersion?: string
    /** UUID of the query presets consequence */
    consequencePresets?: string
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
const data = ref<SeqvarsQueryPresetsConsequence | undefined>(undefined)

/** Shortcut to the number of consequence presets, used for rank. */
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
  return presetSetVersion.seqvarsquerypresetsconsequence_set.length
})

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Fill the data from the store. */
const fillData = () => {
  // Guard against missing preset set version or consequence.
  if (
    props.presetSetVersion === undefined ||
    props.consequencePresets === undefined
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
  const consequencePresets =
    presetSetVersion?.seqvarsquerypresetsconsequence_set.find(
      (elem) => elem.sodar_uuid === props.consequencePresets,
    )
  if (!consequencePresets) {
    emit('message', {
      text: 'Failed to find consequence presets.',
      color: 'error',
    })
    return
  }

  data.value = { ...consequencePresets }
}

/** The consequence groups state. */
const consequenceGroups = computed<
  Record<ConsequenceGroup, ConsequenceGroupState>
>(() => {
  // Guard in case of undefined `data`.
  if (!data.value) {
    return CONSEQUENCE_GROUP_INFOS.reduce(
      (acc, group) => {
        acc[group.key] = { checked: false, indeterminate: false }
        return acc
      },
      {} as Record<ConsequenceGroup, ConsequenceGroupState>,
    )
  }

  const checkedGroups = CONSEQUENCE_GROUP_INFOS.filter((group) =>
    group.valueKeys.every((key) =>
      data.value?.variant_consequences?.includes(key),
    ),
  )
  const indeterminateGroups = CONSEQUENCE_GROUP_INFOS.filter((group) =>
    group.valueKeys.some((key) =>
      data.value?.variant_consequences?.includes(key),
    ),
  )
  return CONSEQUENCE_GROUP_INFOS.reduce(
    (acc, group) => {
      acc[group.key] = {
        checked: checkedGroups.includes(group),
        indeterminate:
          indeterminateGroups.includes(group) && !checkedGroups.includes(group),
      }
      return acc
    },
    {} as Record<ConsequenceGroup, ConsequenceGroupState>,
  )
})

/** Toggles the given consequence group. */
const toggleConsequenceGroup = (key: ConsequenceGroup) => {
  // Guard in case of undefined `data`.
  if (!data.value) {
    return
  }

  if (consequenceGroups.value[key].checked) {
    data.value.variant_consequences = data.value.variant_consequences!.filter(
      (elem) =>
        !CONSEQUENCE_GROUP_INFOS.find(
          (group) => group.key === key,
        )?.valueKeys.includes(elem),
    )
  } else {
    data.value.variant_consequences = data.value.variant_consequences!.concat(
      CONSEQUENCE_GROUP_INFOS.find((group) => group.key === key)?.valueKeys ??
        [],
    )
  }
}

/**
 * Update the consequence presets in the store.
 *
 * Used directly when changing the rank (to minimize UI delay).
 *
 * @param rankDelta The delta to apply to the rank, if any.
 */
const updateConsequencePresets = async (rankDelta: number = 0) => {
  // Guard against missing/readonly/non-draft preset set version or missing consequence.
  if (
    props.consequencePresets === undefined ||
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
    const others = version.seqvarsquerypresetsconsequence_set.filter((elem) => {
      if (elem.sodar_uuid === props.consequencePresets) {
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
        await seqvarsPresetsStore.updateQueryPresetsConsequence(
          props.presetSetVersion,
          other,
        )
      } catch (error) {
        emit('message', {
          text: 'Failed to update consequence presets rank.',
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
    await seqvarsPresetsStore.updateQueryPresetsConsequence(
      props.presetSetVersion,
      data.value,
    )
  } catch (error) {
    emit('message', {
      text: 'Failed to update consequence presets.',
      color: 'error',
    })
  }
}

/**
 * Update the consequence presets in the store -- debounced.
 *
 * Used for updating non-rank fields so that the UI does not lag.
 */
const updateConsequencePresetsDebounced = debounce(
  updateConsequencePresets,
  CATEGORY_PRESETS_DEBOUNCE_WAIT,
  { leading: true, trailing: true },
)

// Load model data from store when the UUID changes.
watch(
  () => props.consequencePresets,
  () => fillData(),
)
// Also, load model data from store when mounted.
onMounted(() => fillData())

// Watch the data and trigger a store update.
watch(data, () => updateConsequencePresetsDebounced(), { deep: true })
</script>

<template>
  <h3>Consequence Presets &raquo;{{ data?.label ?? 'UNDEFINED' }}&laquo;</h3>

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
          @click="updateConsequencePresets(-1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly || data.rank === undefined || data.rank >= maxRank
          "
          @click="updateConsequencePresets(1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <h4 class="pt-3">Distance</h4>

    <v-text-field
      v-model="data.max_distance_to_exon"
      label="Maximal distance to next exon (e.g., 2 for consensus splice sites)"
      type="number"
      hide-details
      clearable
      :disabled="readonly"
    />

    <h4 class="pt-3">Variant Type</h4>

    <v-checkbox
      v-model="data.variant_types"
      value="snv"
      label="SNV"
      density="compact"
      hide-details
      :disabled="readonly"
    />
    <v-checkbox
      v-model="data.variant_types"
      value="indel"
      label="Indel"
      density="compact"
      hide-details
      :disabled="readonly"
    />
    <v-checkbox
      v-model="data.variant_types"
      value="mnv"
      label="MNV"
      density="compact"
      hide-details
      :disabled="readonly"
    />

    <h4 class="pt-3">Transcript Type</h4>

    <v-checkbox
      v-model="data.transcript_types"
      value="coding"
      label="Coding"
      density="compact"
      hide-details
      :disabled="readonly"
    />
    <v-checkbox
      v-model="data.transcript_types"
      value="non_coding"
      label="Non-Coding"
      density="compact"
      hide-details
      :disabled="readonly"
    />

    <h4 class="pt-3">Effect Group</h4>

    <v-checkbox
      v-for="group in CONSEQUENCE_GROUP_INFOS"
      :key="`group-${group.key}`"
      v-model="consequenceGroups[group.key].checked"
      :label="group.label"
      :indeterminate="consequenceGroups[group.key].indeterminate"
      density="compact"
      hide-details
      :disabled="readonly"
      @click="toggleConsequenceGroup(group.key)"
    />

    <h4 class="pt-3">Customize Effects</h4>

    <h5>Coding</h5>

    <v-checkbox
      v-for="consequence in CODING_CONSEQUENCES"
      :key="`consequence-${consequence.key}`"
      v-model="data.variant_consequences"
      :value="consequence.key"
      :label="consequence.label"
      density="compact"
      hide-details
      :disabled="readonly"
    />

    <h5>Off-Exomes</h5>

    <v-checkbox
      v-for="consequence in OFF_EXOMES_CONSEQUENCES"
      :key="`consequence-${consequence.key}`"
      v-model="data.variant_consequences"
      :value="consequence.key"
      :label="consequence.label"
      density="compact"
      hide-details
      :disabled="readonly"
    />

    <h5>Non-coding</h5>

    <v-checkbox
      v-for="consequence in NON_CODING_CONSEQUENCES"
      :key="`consequence-${consequence.key}`"
      v-model="data.variant_consequences"
      :value="consequence.key"
      :label="consequence.label"
      density="compact"
      hide-details
      :disabled="readonly"
    />

    <h5>Splicing</h5>

    <v-checkbox
      v-for="consequence in SPLICING_CONSEQUENCES"
      :key="`consequence-${consequence.key}`"
      v-model="data.variant_consequences"
      :value="consequence.key"
      :label="consequence.label"
      density="compact"
      hide-details
      :disabled="readonly"
    />
  </v-form>
</template>
