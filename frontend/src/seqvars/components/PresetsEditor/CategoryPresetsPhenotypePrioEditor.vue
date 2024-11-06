<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { SeqvarsQueryPresetsPhenotypePrio } from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'
import { VForm } from 'vuetify/lib/components/index.mjs'

import {
  invalidateSeqvarQueryPresetsSetVersionKeys,
  useSeqvarQueryPresetsSetVersionRetrieveQuery,
} from '@/seqvars/queries/seqvarQueryPresetSetVersion'
import {
  useSeqvarsQueryPresetsPhenotypePrioRetrieveQuery,
  useSeqvarsQueryPresetsPhenotypePrioUpdateMutation,
} from '@/seqvars/queries/seqvarQueryPresetsPhenotypePrio'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the current presets set. */
    presetSet?: string
    /** UUID of the current preset set version. */
    presetSetVersion?: string
    /** UUID of the query presets phenotype prio */
    phenotypePrioPresets?: string
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
/** PhenotypePrio presets UUID as `ComputedRef` for queries. */
const presetsPhenotypePrioUuid = computed<string | undefined>(() => {
  return props.phenotypePrioPresets
})

/** Query with the currently selected presets set version. */
const presetsSetVersionRetrieveRes =
  useSeqvarQueryPresetsSetVersionRetrieveQuery({
    presetsSetUuid,
    presetsSetVersionUuid,
  })
/** Query with the currently selected phenotypePrio presets. */
const presetsPhenotypePrioRetrieveRes =
  useSeqvarsQueryPresetsPhenotypePrioRetrieveQuery({
    presetsSetVersionUuid,
    presetsPhenotypePrioUuid,
  })
/** Mutation for updating the phenotypePrio presets. */
const phenotypePrioPresetsUpdate =
  useSeqvarsQueryPresetsPhenotypePrioUpdateMutation()

/** Shortcut to the number of phenotypePrio presets, used for rank. */
const maxRank = computed<number>(
  () =>
    presetsSetVersionRetrieveRes.data.value
      ?.seqvarsquerypresetsphenotypeprio_set.length ?? 0,
)

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Helper to apply a patch to the current `presetsPhenotypePrioRetrieveRes.data.value`. */
const applyMutation = async (
  patch: Partial<SeqvarsQueryPresetsPhenotypePrio>,
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
    presetsPhenotypePrioRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value.status !==
      PresetSetVersionState.DRAFT
  ) {
    return
  } else {
    patch.rank = presetsPhenotypePrioRetrieveRes.data.value.rank
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
      const others = version.seqvarsquerypresetsphenotypeprio_set.filter(
        (elem) => {
          if (elem.sodar_uuid === props.phenotypePrioPresets) {
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
          await phenotypePrioPresetsUpdate.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsphenotypeprio: other.sodar_uuid,
            },
            body: {
              ...other,
              rank: newOtherRank,
            },
          })
        } catch (error) {
          emit('message', {
            text: `Failed to update other phenotypePrio presets rank: ${error}`,
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
    await phenotypePrioPresetsUpdate.mutateAsync({
      path: {
        querypresetssetversion: props.presetSetVersion,
        querypresetsphenotypeprio:
          presetsPhenotypePrioRetrieveRes.data.value.sodar_uuid,
      },
      body: {
        ...presetsPhenotypePrioRetrieveRes.data.value,
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
      text: `Failed to update phenotypePrio presets: ${error}`,
      color: 'error',
    })
  }
}
</script>

<template>
  <h4>
    Phenotype Prio Presets &raquo;{{
      presetsPhenotypePrioRetrieveRes.data.value?.label ?? 'UNDEFINED'
    }}&laquo;
  </h4>

  <v-skeleton-loader
    v-if="presetsPhenotypePrioRetrieveRes.status.value !== 'success'"
    type="article"
  />

  <v-form v-else ref="formRef">
    <v-text-field
      :model-value="presetsPhenotypePrioRetrieveRes.data.value?.label"
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
            presetsPhenotypePrioRetrieveRes.data.value?.rank === undefined ||
            presetsPhenotypePrioRetrieveRes.data.value?.rank <= 1
          "
          @click="applyMutation({}, -1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly ||
            presetsPhenotypePrioRetrieveRes.data.value?.rank === undefined ||
            presetsPhenotypePrioRetrieveRes.data.value?.rank >= maxRank
          "
          @click="applyMutation({}, 1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <v-sheet class="text-center font-italic bg-grey-lighten-3 pa-3 mt-3">
      Phenotype priorization presets editor is not implemented yet.
    </v-sheet>

    <div>
      Enabled:
      {{
        presetsPhenotypePrioRetrieveRes.data.value?.phenotype_prio_enabled
          ? 'Yes'
          : 'No'
      }}
    </div>
    <div>
      Algorithm:
      {{
        presetsPhenotypePrioRetrieveRes.data.value?.phenotype_prio_algorithm ??
        'N/A'
      }}
    </div>
    <div>
      Terms:
      <span
        v-if="presetsPhenotypePrioRetrieveRes.data.value?.terms?.length === 0"
        class="text-grey-darken-2"
      >
        N/A
      </span>
      <span v-else>
        <v-chip
          v-for="(term, index) in presetsPhenotypePrioRetrieveRes.data.value
            ?.terms ?? []"
          :key="index"
        >
          {{ term }}
        </v-chip>
      </span>
    </div>
  </v-form>
</template>
