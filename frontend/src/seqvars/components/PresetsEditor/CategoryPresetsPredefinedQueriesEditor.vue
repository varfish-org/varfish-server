<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { SeqvarsPredefinedQuery } from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'
import { VForm } from 'vuetify/lib/components/index.mjs'

import {
  invalidateSeqvarQueryPresetsSetVersionKeys,
  useSeqvarQueryPresetsSetVersionRetrieveQuery,
} from '@/seqvars/queries/seqvarQueryPresetSetVersion'
import {
  useSeqvarsPredefinedQueryRetrieveQuery,
  useSeqvarsPredefinedQueryUpdateMutation,
} from '@/seqvars/queries/seqvarQueryPresetsPredefinedQuery'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

import { GENOTYPE_PRESET_LABELS } from './lib'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the current presets set. */
    presetSet?: string
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
/** PredefinedQueries presets UUID as `ComputedRef` for queries. */
const presetsPredefinedQueryUuid = computed<string | undefined>(() => {
  return props.predefinedQueriesPresets
})

/** Query with the currently selected presets set version. */
const presetsSetVersionRetrieveRes =
  useSeqvarQueryPresetsSetVersionRetrieveQuery({
    presetsSetUuid,
    presetsSetVersionUuid,
  })
/** Query with the currently selected predefinedQueriesPresets presets. */
const presetsPredefinedQueryRetrieveRes =
  useSeqvarsPredefinedQueryRetrieveQuery({
    presetsSetVersionUuid,
    presetsPredefinedQueryUuid,
  })
/** Mutation for updating the predefinedQueriesPresets presets. */
const predefinedQueriesPresetsUpdate = useSeqvarsPredefinedQueryUpdateMutation()

/** Shortcut to the number of predefinedQueriesPresets presets, used for rank. */
const maxRank = computed<number>(
  () =>
    presetsSetVersionRetrieveRes.data.value?.seqvarspredefinedquery_set
      .length ?? 0,
)

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Helper to apply a patch to the current `presetsPredefinedQueryRetrieveRes.data.value`. */
const applyMutation = async (
  patch: Partial<SeqvarsPredefinedQuery>,
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
    presetsPredefinedQueryRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value.status !==
      PresetSetVersionState.DRAFT
  ) {
    return
  } else {
    patch.rank = presetsPredefinedQueryRetrieveRes.data.value.rank
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
      const others = version.seqvarspredefinedquery_set.filter((elem) => {
        if (elem.sodar_uuid === props.predefinedQueriesPresets) {
          return false
        }
        if (rankDelta < 0) {
          return (elem.rank ?? 0) < (patch?.rank ?? 0)
        } else {
          return (elem.rank ?? 0) > (patch?.rank ?? 0)
        }
      })
      others.sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
      // Then, pick the other item to flip ranks with.
      const other = { ...others[rankDelta < 0 ? others.length - 1 : 0] }
      // Store the other's rank in `data.rank` and update other via API.
      if (!!other) {
        const newOtherRank = patch.rank
        patch.rank = other.rank
        other.rank = newOtherRank
        try {
          await predefinedQueriesPresetsUpdate.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              predefinedquery: other.sodar_uuid,
            },
            body: {
              ...other,
              rank: newOtherRank,
            },
          })
        } catch (error) {
          emit('message', {
            text: `Failed to update other predefinedQueriesPresets presets rank: ${error}`,
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
    await predefinedQueriesPresetsUpdate.mutateAsync({
      path: {
        querypresetssetversion: props.presetSetVersion,
        predefinedquery:
          presetsPredefinedQueryRetrieveRes.data.value.sodar_uuid,
      },
      body: {
        ...presetsPredefinedQueryRetrieveRes.data.value,
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
      text: `Failed to update predefinedQueriesPresets presets: ${error}`,
      color: 'error',
    })
  }
}

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
</script>

<template>
  <h4>
    Predefined Queries Presets &raquo;{{
      presetsPredefinedQueryRetrieveRes.data.value?.label ?? 'UNDEFINED'
    }}&laquo;
  </h4>

  <v-skeleton-loader
    v-if="presetsPredefinedQueryRetrieveRes.status.value !== 'success'"
    type="article"
  />

  <v-form v-else ref="formRef">
    <v-text-field
      :model-value="presetsPredefinedQueryRetrieveRes.data.value?.label"
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
            presetsPredefinedQueryRetrieveRes.data.value?.rank === undefined ||
            presetsPredefinedQueryRetrieveRes.data.value?.rank <= 1
          "
          @click="applyMutation({}, -1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly ||
            presetsPredefinedQueryRetrieveRes.data.value?.rank === undefined ||
            presetsPredefinedQueryRetrieveRes.data.value?.rank >= maxRank
          "
          @click="applyMutation({}, 1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <div class="border-t-thin my-3"></div>

    <v-checkbox
      :model-value="
        presetsPredefinedQueryRetrieveRes.data.value?.included_in_sop
      "
      label="Include in SOP"
      hint="The queries that are included in SOP can be auto-started together."
      density="compact"
      persistent-hint
      :disabled="readonly"
      @update:model-value="
        applyMutation({
          included_in_sop:
            !presetsPredefinedQueryRetrieveRes.data.value?.included_in_sop,
        })
      "
    />

    <div class="border-t-thin my-3"></div>

    <v-select
      :model-value="
        presetsPredefinedQueryRetrieveRes.data.value?.genotype!.choice
      "
      label="Genotype Preset"
      :items="Object.keys(GENOTYPE_PRESET_LABELS)"
      :item-title="
        (key: keyof typeof GENOTYPE_PRESET_LABELS) =>
          GENOTYPE_PRESET_LABELS[key]
      "
      :disabled="readonly"
    />

    <v-select
      :model-value="presetsPredefinedQueryRetrieveRes.data.value?.quality"
      label="Quality Preset"
      :items="
        extractItems(
          presetsSetVersionRetrieveRes.data.value
            ?.seqvarsquerypresetsquality_set ?? [],
        )
      "
      item-props
      :disabled="readonly"
      @update:model-value="
        (quality) => {
          applyMutation({
            quality,
          })
        }
      "
    />

    <v-select
      :model-value="presetsPredefinedQueryRetrieveRes.data.value?.frequency"
      label="Frequency Preset"
      :items="
        extractItems(
          presetsSetVersionRetrieveRes.data.value
            ?.seqvarsquerypresetsfrequency_set ?? [],
        )
      "
      item-props
      :disabled="readonly"
      @update:model-value="
        (frequency) => {
          applyMutation({
            frequency,
          })
        }
      "
    />

    <v-select
      :model-value="presetsPredefinedQueryRetrieveRes.data.value?.consequence"
      label="Consequence Preset"
      :items="
        extractItems(
          presetsSetVersionRetrieveRes.data.value
            ?.seqvarsquerypresetsconsequence_set ?? [],
        )
      "
      item-props
      :disabled="readonly"
      @update:model-value="
        (consequence) => {
          applyMutation({
            consequence,
          })
        }
      "
    />

    <v-select
      :model-value="presetsPredefinedQueryRetrieveRes.data.value?.locus"
      label="Locus Preset"
      :items="
        extractItems(
          presetsSetVersionRetrieveRes.data.value
            ?.seqvarsquerypresetslocus_set ?? [],
        )
      "
      item-props
      :disabled="readonly"
      @update:model-value="
        (locus) => {
          applyMutation({
            locus,
          })
        }
      "
    />

    <v-select
      :model-value="presetsPredefinedQueryRetrieveRes.data.value?.phenotypeprio"
      label="Phenotype Priority Preset"
      :items="
        extractItems(
          presetsSetVersionRetrieveRes.data.value
            ?.seqvarsquerypresetsphenotypeprio_set ?? [],
        )
      "
      item-props
      :disabled="readonly"
      @update:model-value="
        (phenotypeprio) => {
          applyMutation({
            phenotypeprio,
          })
        }
      "
    />

    <v-select
      :model-value="presetsPredefinedQueryRetrieveRes.data.value?.variantprio"
      label="Variant Priority Preset"
      :items="
        extractItems(
          presetsSetVersionRetrieveRes.data.value
            ?.seqvarsquerypresetsvariantprio_set ?? [],
        )
      "
      item-props
      :disabled="readonly"
      @update:model-value="
        (variantprio) => {
          applyMutation({
            variantprio,
          })
        }
      "
    />

    <v-select
      :model-value="presetsPredefinedQueryRetrieveRes.data.value?.clinvar"
      label="Clinvar Preset"
      :items="
        extractItems(
          presetsSetVersionRetrieveRes.data.value
            ?.seqvarsquerypresetsclinvar_set ?? [],
        )
      "
      item-props
      :disabled="readonly"
      @update:model-value="
        (clinvar) => {
          applyMutation({
            clinvar,
          })
        }
      "
    />

    <v-select
      :model-value="presetsPredefinedQueryRetrieveRes.data.value?.columns"
      label="Columns Preset"
      :items="
        extractItems(
          presetsSetVersionRetrieveRes.data.value
            ?.seqvarsquerypresetscolumns_set ?? [],
        )
      "
      item-props
      :disabled="readonly"
      @update:model-value="
        (columns) => {
          applyMutation({
            columns,
          })
        }
      "
    />
  </v-form>
</template>
