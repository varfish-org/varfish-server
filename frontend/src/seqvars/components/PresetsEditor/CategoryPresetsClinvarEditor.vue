<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { SeqvarsQueryPresetsClinvar } from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'
import { VForm } from 'vuetify/lib/components/index.mjs'

import {
  invalidateSeqvarQueryPresetsSetVersionKeys,
  useSeqvarQueryPresetsSetVersionRetrieveQuery,
} from '@/seqvars/queries/seqvarQueryPresetSetVersion'
import {
  useSeqvarsQueryPresetsClinvarRetrieveQuery,
  useSeqvarsQueryPresetsClinvarUpdateMutation,
} from '@/seqvars/queries/seqvarQueryPresetsClinvar'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the current presets set. */
    presetSet?: string
    /** UUID of the current preset set version. */
    presetSetVersion?: string
    /** UUID of the query presets clinvar */
    clinvarPresets?: string
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

const LABELS = [
  'pathogenic',
  'likely_pathogenic',
  'uncertain_significance',
  'likely_benign',
  'benign',
]

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
/** Clinvar presets UUID as `ComputedRef` for queries. */
const presetsClinvarUuid = computed<string | undefined>(() => {
  return props.clinvarPresets
})

/** Query with the currently selected presets set version. */
const presetsSetVersionRetrieveRes =
  useSeqvarQueryPresetsSetVersionRetrieveQuery({
    presetsSetUuid,
    presetsSetVersionUuid,
  })
/** Query with the currently selected clinvar presets. */
const presetsClinvarRetrieveRes = useSeqvarsQueryPresetsClinvarRetrieveQuery({
  presetsSetVersionUuid,
  presetsClinvarUuid,
})
/** Mutation for updating the clinvar presets. */
const clinvarPresetsUpdate = useSeqvarsQueryPresetsClinvarUpdateMutation()

/** Shortcut to the number of clinvar presets, used for rank. */
const maxRank = computed<number>(
  () =>
    presetsSetVersionRetrieveRes.data.value?.seqvarsquerypresetsclinvar_set
      .length ?? 0,
)

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Helper to apply a patch to the current `presetsClinvarRetrieveRes.data.value`. */
const applyMutation = async (
  patch: Partial<SeqvarsQueryPresetsClinvar>,
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
    presetsClinvarRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value.status !==
      PresetSetVersionState.DRAFT
  ) {
    return
  } else {
    patch.rank = presetsClinvarRetrieveRes.data.value.rank
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
      const others = version.seqvarsquerypresetsclinvar_set.filter((elem) => {
        if (elem.sodar_uuid === props.clinvarPresets) {
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
          await clinvarPresetsUpdate.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsclinvar: other.sodar_uuid,
            },
            body: {
              ...other,
              rank: newOtherRank,
            },
          })
        } catch (error) {
          emit('message', {
            text: `Failed to update other clinvar presets rank: ${error}`,
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
    await clinvarPresetsUpdate.mutateAsync({
      path: {
        querypresetssetversion: props.presetSetVersion,
        querypresetsclinvar: presetsClinvarRetrieveRes.data.value.sodar_uuid,
      },
      body: {
        ...presetsClinvarRetrieveRes.data.value,
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
      text: `Failed to update clinvar presets: ${error}`,
      color: 'error',
    })
  }
}
</script>

<template>
  <h4>
    Clinvar Presets &raquo;{{
      presetsClinvarRetrieveRes.data.value?.label ?? 'UNDEFINED'
    }}&laquo;
  </h4>

  <v-skeleton-loader
    v-if="!presetsClinvarRetrieveRes.data.value"
    type="article"
  />
  <v-form v-else ref="formRef">
    <v-text-field
      :model-value="presetsClinvarRetrieveRes.data.value?.label"
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
            presetsClinvarRetrieveRes.data.value?.rank === undefined ||
            presetsClinvarRetrieveRes.data.value?.rank <= 1
          "
          @click="applyMutation({}, -1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly ||
            presetsClinvarRetrieveRes.data.value?.rank === undefined ||
            presetsClinvarRetrieveRes.data.value?.rank >= maxRank
          "
          @click="applyMutation({}, 1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <v-checkbox
      :model-value="
        presetsClinvarRetrieveRes.data.value?.clinvar_presence_required
      "
      label="ClinVar presence required"
      hide-details
      density="compact"
      :disabled="readonly"
      @update:model-value="
        applyMutation({
          clinvar_presence_required:
            !presetsClinvarRetrieveRes.data.value?.clinvar_presence_required,
        })
      "
    />

    <div class="border-t-thin my-3"></div>

    <div>
      <v-checkbox
        v-for="label in LABELS"
        :key="label"
        :model-value="
          presetsClinvarRetrieveRes.data.value
            .clinvar_germline_aggregate_description ?? []
        "
        :label="label"
        :value="label"
        hide-details
        density="compact"
        :disabled="readonly"
        @update:model-value="
          (clinvar_germline_aggregate_description) => {
            applyMutation({
              clinvar_germline_aggregate_description:
                clinvar_germline_aggregate_description ?? undefined,
            })
          }
        "
      />
    </div>

    <div class="border-t-thin my-3"></div>

    <v-checkbox
      :model-value="
        presetsClinvarRetrieveRes.data.value?.allow_conflicting_interpretations
      "
      label="Allow conflicting interpretations"
      hide-details
      density="compact"
      :disabled="readonly"
      @update:model-value="
        applyMutation({
          allow_conflicting_interpretations:
            !presetsClinvarRetrieveRes.data.value
              ?.allow_conflicting_interpretations,
        })
      "
    />
  </v-form>
</template>
