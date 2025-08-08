<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { SeqvarsQueryPresetsConsequence } from '@varfish-org/varfish-api/lib'
import { data } from 'jquery'
import { computed, ref } from 'vue'
import { VForm } from 'vuetify/lib/components/index.mjs'

import {
  invalidateSeqvarQueryPresetsSetVersionKeys,
  useSeqvarQueryPresetsSetVersionRetrieveQuery,
} from '@/seqvars/queries/seqvarQueryPresetSetVersion'
import {
  useSeqvarsQueryPresetsConsequenceRetrieveQuery,
  useSeqvarsQueryPresetsConsequenceUpdateMutation,
} from '@/seqvars/queries/seqvarQueryPresetsConsequence'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

import {
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
    /** UUID of the current presets set. */
    presetSet?: string
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

/** The `QueryClient` for explicit invalidation.*/
const queryClient = useQueryClient()

/** Presets set UUID as `ComputedRef` for queries. */
const presetsSetUuid = computed<string | undefined>(() => {
  return props.presetSet
})
/** Presets set version UUID as `ComputedRef` for queries. */
const presetsSetVersionUuid = computed<string | undefined>(() => {
  return props.presetSetVersion
})
/** Consequence presets UUID as `ComputedRef` for queries. */
const presetsConsequenceUuid = computed<string | undefined>(() => {
  return props.consequencePresets
})

/** Query with the currently selected presets set version. */
const presetsSetVersionRetrieveRes =
  useSeqvarQueryPresetsSetVersionRetrieveQuery({
    presetsSetUuid,
    presetsSetVersionUuid,
  })
/** Query with the currently selected consequence presets. */
const presetsConsequenceRetrieveRes =
  useSeqvarsQueryPresetsConsequenceRetrieveQuery({
    presetsSetVersionUuid,
    presetsConsequenceUuid,
  })
/** Mutation for updating the consequence presets. */
const consequencePresetsUpdate =
  useSeqvarsQueryPresetsConsequenceUpdateMutation()

/** Shortcut to the number of consequence presets, used for rank. */
const maxRank = computed<number>(
  () =>
    presetsSetVersionRetrieveRes.data.value?.seqvarsquerypresetsconsequence_set
      .length ?? 0,
)

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Helper to apply a patch to the current `presetsConsequenceRetrieveRes.data.value`. */
const applyMutation = async (
  patch: Partial<SeqvarsQueryPresetsConsequence>,
  rankDelta: number = 0,
) => {
  // Guard against invalid form data.
  const validateResult = await formRef.value?.validate()
  if (validateResult?.valid !== true) {
    return
  }
  // Short-circuit if patch is undefined or presets version undefine dor not in draft state.
  if (
    props.presetSet === undefined ||
    props.presetSetVersion === undefined ||
    presetsConsequenceRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value.status !==
      PresetSetVersionState.DRAFT
  ) {
    return
  } else {
    patch.rank = presetsConsequenceRetrieveRes.data.value.rank
  }

  // Helper to update the rank of the other item as well.
  const updateOtherItemRank = async () => {
    if (props.presetSetVersion !== undefined && rankDelta !== 0) {
      const version = presetsSetVersionRetrieveRes.data.value
      if (
        version === undefined ||
        patch.rank === undefined ||
        patch.rank + rankDelta < 1 ||
        patch.rank + rankDelta > maxRank.value
      ) {
        // Guard against invalid or missing data.
        return
      }
      // Find the next smaller or larger item, sort by rank.
      const others = version.seqvarsquerypresetsconsequence_set.filter(
        (elem) => {
          if (elem.sodar_uuid === props.consequencePresets) {
            return false
          }
          if (rankDelta < 0) {
            return (elem.rank ?? 0) < (patch?.rank ?? 0)
          } else {
            return (elem.rank ?? 0) > (patch?.rank ?? 0)
          }
        },
      )
      others.sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
      // Then, pick the other item to flip ranks with.
      const other = { ...others[rankDelta < 0 ? others.length - 1 : 0] }
      // Store the other's rank in `data.rank` and update other via API.
      if (!!other) {
        const newOtherRank = patch.rank
        patch.rank = other.rank
        other.rank = newOtherRank
        try {
          await consequencePresetsUpdate.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsconsequence: other.sodar_uuid,
            },
            body: {
              ...other,
              rank: newOtherRank,
            },
          })
        } catch (error) {
          emit('message', {
            text: `Failed to update other consequence presets rank: ${error}`,
            color: 'error',
          })
        }
      }
    }
  }

  // First, apply rank update to other data object and to patch if applicable.
  // On success, the patch to the data object.
  try {
    await updateOtherItemRank()
    await consequencePresetsUpdate.mutateAsync({
      path: {
        querypresetssetversion: props.presetSetVersion,
        querypresetsconsequence:
          presetsConsequenceRetrieveRes.data.value.sodar_uuid,
      },
      body: {
        ...presetsConsequenceRetrieveRes.data.value,
        ...patch,
      },
    })
    // Explicitely invalidate the query presets set version as the title and rank
    // can change and the version stores the category presets as well.
    invalidateSeqvarQueryPresetsSetVersionKeys(queryClient, {
      querypresetsset: props.presetSet,
      querypresetssetversion: props.presetSetVersion,
    })
  } catch (error) {
    emit('message', {
      text: `Failed to update consequence presets: ${error}`,
      color: 'error',
    })
  }
}

/** The consequence groups state. */
const consequenceGroups = computed<
  Record<ConsequenceGroup, ConsequenceGroupState>
>(() => {
  // Guard in case of undefined `data`.
  if (!presetsConsequenceRetrieveRes.data.value) {
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
      presetsConsequenceRetrieveRes.data.value?.variant_consequences?.includes(
        key,
      ),
    ),
  )
  const indeterminateGroups = CONSEQUENCE_GROUP_INFOS.filter((group) =>
    group.valueKeys.some((key) =>
      presetsConsequenceRetrieveRes.data.value?.variant_consequences?.includes(
        key,
      ),
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
const toggleConsequenceGroup = async (key: ConsequenceGroup) => {
  // Guard in case of undefined `data`.
  if (!presetsConsequenceRetrieveRes.data.value) {
    return
  }

  if (consequenceGroups.value[key].checked) {
    await applyMutation({
      variant_consequences:
        presetsConsequenceRetrieveRes.data.value.variant_consequences!.filter(
          (elem) =>
            !CONSEQUENCE_GROUP_INFOS.find(
              (group) => group.key === key,
            )?.valueKeys.includes(elem),
        ),
    })
  } else {
    await applyMutation({
      variant_consequences:
        presetsConsequenceRetrieveRes.data.value.variant_consequences!.concat(
          CONSEQUENCE_GROUP_INFOS.find((group) => group.key === key)
            ?.valueKeys ?? [],
        ),
    })
  }
}
</script>

<template>
  <h3>
    Consequence Presets &raquo;{{
      presetsConsequenceRetrieveRes.data.value?.label ?? 'UNDEFINED'
    }}&laquo;
  </h3>

  <v-skeleton-loader v-if="!data" type="article" />
  <v-form v-else ref="formRef">
    <v-text-field
      :model-value="presetsConsequenceRetrieveRes.data.value?.label"
      :rules="[rules.required]"
      label="Label"
      clearable
      :disabled="readonly"
      @update:model-value="
        (label) =>
          applyMutation({
            label,
          })
      "
    />

    <div>
      <v-btn-group variant="outlined" divided>
        <v-btn
          prepend-icon="mdi-arrow-up-circle-outline"
          :disabled="
            props.readonly ||
            presetsConsequenceRetrieveRes.data.value?.rank === undefined ||
            presetsConsequenceRetrieveRes.data.value?.rank <= 1
          "
          @click="applyMutation({}, -1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly ||
            presetsConsequenceRetrieveRes.data.value?.rank === undefined ||
            presetsConsequenceRetrieveRes.data.value?.rank >= maxRank
          "
          @click="applyMutation({}, 1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <h4 class="pt-3">Distance</h4>

    <v-number-input
      :model-value="
        presetsConsequenceRetrieveRes.data.value?.max_distance_to_exon
      "
      label="Maximal distance to next exon (e.g., 2 for consensus splice sites)"
      clearable
      control-variant="stacked"
      hide-details
      :disabled="readonly"
      @update:model-value="
        (max_distance_to_exon) =>
          applyMutation({
            max_distance_to_exon,
          })
      "
    />

    <h4 class="pt-3">Variant Type</h4>

    <v-checkbox
      :model-value="presetsConsequenceRetrieveRes.data.value?.variant_types"
      value="snv"
      label="SNV"
      density="compact"
      hide-details
      :disabled="readonly"
      @update:model-value="
        (variant_types) =>
          applyMutation({
            variant_types: variant_types ?? undefined,
          })
      "
    />
    <v-checkbox
      :model-value="presetsConsequenceRetrieveRes.data.value?.variant_types"
      value="indel"
      label="Indel"
      density="compact"
      hide-details
      :disabled="readonly"
      @update:model-value="
        (variant_types) =>
          applyMutation({
            variant_types: variant_types ?? undefined,
          })
      "
    />
    <v-checkbox
      :model-value="presetsConsequenceRetrieveRes.data.value?.variant_types"
      value="mnv"
      label="MNV"
      density="compact"
      hide-details
      :disabled="readonly"
      @update:model-value="
        (variant_types) =>
          applyMutation({
            variant_types: variant_types ?? undefined,
          })
      "
    />

    <h4 class="pt-3">Transcript Type</h4>

    <v-checkbox
      :model-value="presetsConsequenceRetrieveRes.data.value?.transcript_types"
      value="coding"
      label="Coding"
      density="compact"
      hide-details
      :disabled="readonly"
      @update:model-value="
        (transcript_types) =>
          applyMutation({
            transcript_types: transcript_types ?? undefined,
          })
      "
    />
    <v-checkbox
      :model-value="presetsConsequenceRetrieveRes.data.value?.transcript_types"
      value="non_coding"
      label="Non-Coding"
      density="compact"
      hide-details
      :disabled="readonly"
      @update:model-value="
        (transcript_types) =>
          applyMutation({
            transcript_types: transcript_types ?? undefined,
          })
      "
    />

    <h4 class="pt-3">Effect Group</h4>

    <v-checkbox
      v-for="group in CONSEQUENCE_GROUP_INFOS"
      :key="`group-${group.key}`"
      :model-value="consequenceGroups[group.key].checked"
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
      :model-value="
        presetsConsequenceRetrieveRes.data.value?.variant_consequences ?? []
      "
      :value="consequence.key"
      :label="consequence.label"
      density="compact"
      hide-details
      :disabled="readonly"
      @update:model-value="
        (variant_consequences) => {
          applyMutation({
            variant_consequences: variant_consequences ?? undefined,
          })
        }
      "
    />

    <h5>Off-Exomes</h5>

    <v-checkbox
      v-for="consequence in OFF_EXOMES_CONSEQUENCES"
      :key="`consequence-${consequence.key}`"
      :model-value="
        presetsConsequenceRetrieveRes.data.value?.variant_consequences ?? []
      "
      :value="consequence.key"
      :label="consequence.label"
      density="compact"
      hide-details
      :disabled="readonly"
      @update:model-value="
        (variant_consequences) =>
          applyMutation({
            variant_consequences: variant_consequences ?? undefined,
          })
      "
    />

    <h5>Non-coding</h5>

    <v-checkbox
      v-for="consequence in NON_CODING_CONSEQUENCES"
      :key="`consequence-${consequence.key}`"
      :model-value="
        presetsConsequenceRetrieveRes.data.value?.variant_consequences ?? []
      "
      :value="consequence.key"
      :label="consequence.label"
      density="compact"
      hide-details
      :disabled="readonly"
      @update:model-value="
        (variant_consequences) =>
          applyMutation({
            variant_consequences: variant_consequences ?? undefined,
          })
      "
    />

    <h5>Splicing</h5>

    <v-checkbox
      v-for="consequence in SPLICING_CONSEQUENCES"
      :key="`consequence-${consequence.key}`"
      :model-value="
        presetsConsequenceRetrieveRes.data.value?.variant_consequences
      "
      :value="consequence.key"
      :label="consequence.label"
      density="compact"
      hide-details
      :disabled="readonly"
      @update:model-value="
        (variant_consequences) =>
          applyMutation({
            variant_consequences: variant_consequences ?? undefined,
          })
      "
    />
  </v-form>
</template>
