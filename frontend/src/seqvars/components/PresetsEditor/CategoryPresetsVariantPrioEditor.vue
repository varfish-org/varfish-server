<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { SeqvarsQueryPresetsVariantPrio } from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'
import { VForm } from 'vuetify/lib/components/index.mjs'

import {
  invalidateSeqvarQueryPresetsSetVersionKeys,
  useSeqvarQueryPresetsSetVersionRetrieveQuery,
} from '@/seqvars/queries/seqvarQueryPresetSetVersion'
import {
  useSeqvarsQueryPresetsVariantPrioRetrieveQuery,
  useSeqvarsQueryPresetsVariantPrioUpdateMutation,
} from '@/seqvars/queries/seqvarQueryPresetsVariantPrio'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the current presets set. */
    presetSet?: string
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
/** VariantPrio presets UUID as `ComputedRef` for queries. */
const presetsVariantPrioUuid = computed<string | undefined>(() => {
  return props.variantPrioPresets
})

/** Query with the currently selected presets set version. */
const presetsSetVersionRetrieveRes =
  useSeqvarQueryPresetsSetVersionRetrieveQuery({
    presetsSetUuid,
    presetsSetVersionUuid,
  })
/** Query with the currently selected variantPrio presets. */
const presetsVariantPrioRetrieveRes =
  useSeqvarsQueryPresetsVariantPrioRetrieveQuery({
    presetsSetVersionUuid,
    presetsVariantPrioUuid,
  })
/** Mutation for updating the variantPrio presets. */
const variantPrioPresetsUpdate =
  useSeqvarsQueryPresetsVariantPrioUpdateMutation()

/** Shortcut to the number of variantPrio presets, used for rank. */
const maxRank = computed<number>(
  () =>
    presetsSetVersionRetrieveRes.data.value?.seqvarsquerypresetsvariantprio_set
      .length ?? 0,
)

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Helper to apply a patch to the current `presetsVariantPrioRetrieveRes.data.value`. */
const applyMutation = async (
  patch: Partial<SeqvarsQueryPresetsVariantPrio>,
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
    presetsVariantPrioRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value.status !==
      PresetSetVersionState.DRAFT
  ) {
    return
  } else {
    patch.rank = presetsVariantPrioRetrieveRes.data.value.rank
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
      const others = version.seqvarsquerypresetsvariantprio_set.filter(
        (elem) => {
          if (elem.sodar_uuid === props.variantPrioPresets) {
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
          await variantPrioPresetsUpdate.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsvariantprio: other.sodar_uuid,
            },
            body: {
              ...other,
              rank: newOtherRank,
            },
          })
        } catch (error) {
          emit('message', {
            text: `Failed to update other variantPrio presets rank: ${error}`,
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
    await variantPrioPresetsUpdate.mutateAsync({
      path: {
        querypresetssetversion: props.presetSetVersion,
        querypresetsvariantprio:
          presetsVariantPrioRetrieveRes.data.value.sodar_uuid,
      },
      body: {
        ...presetsVariantPrioRetrieveRes.data.value,
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
      text: `Failed to update variantPrio presets: ${error}`,
      color: 'error',
    })
  }
}
</script>

<template>
  <h4>
    Variant Priorization Presets &raquo;{{
      presetsVariantPrioRetrieveRes.data.value?.label ?? 'UNDEFINED'
    }}&laquo;
  </h4>

  <v-skeleton-loader
    v-if="presetsVariantPrioRetrieveRes.status.value !== 'success'"
    type="article"
  />

  <v-form v-else ref="formRef">
    <v-text-field
      :model-value="presetsVariantPrioRetrieveRes.data.value?.label"
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
            presetsVariantPrioRetrieveRes.data.value?.rank === undefined ||
            presetsVariantPrioRetrieveRes.data.value?.rank <= 1
          "
          @click="applyMutation({}, -1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly ||
            presetsVariantPrioRetrieveRes.data.value?.rank === undefined ||
            presetsVariantPrioRetrieveRes.data.value?.rank >= maxRank
          "
          @click="applyMutation({}, 1)"
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
      {{
        presetsVariantPrioRetrieveRes.data.value?.variant_prio_enabled
          ? 'Yes'
          : 'No'
      }}
    </div>
    <div>
      Services/Algorithms:
      <span
        v-if="presetsVariantPrioRetrieveRes.data.value?.services?.length === 0"
        class="text-grey-darken-2"
      >
        N/A
      </span>
      <span v-else>
        <v-chip
          v-for="(service, index) in presetsVariantPrioRetrieveRes.data.value
            ?.services ?? []"
          :key="index"
        >
          {{ service.name }} ({{ service.version }})
        </v-chip>
      </span>
    </div>
  </v-form>
</template>
