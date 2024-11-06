<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { SeqvarsQueryPresetsQuality } from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'
import { VForm } from 'vuetify/lib/components/index.mjs'

import {
  invalidateSeqvarQueryPresetsSetVersionKeys,
  useSeqvarQueryPresetsSetVersionRetrieveQuery,
} from '@/seqvars/queries/seqvarQueryPresetSetVersion'
import {
  useSeqvarsQueryPresetsQualityRetrieveQuery,
  useSeqvarsQueryPresetsQualityUpdateMutation,
} from '@/seqvars/queries/seqvarQueryPresetsQuality'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the current presets set. */
    presetSet?: string
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
/** Quality presets UUID as `ComputedRef` for queries. */
const presetsQualityUuid = computed<string | undefined>(() => {
  return props.qualityPresets
})

/** Query with the currently selected presets set version. */
const presetsSetVersionRetrieveRes =
  useSeqvarQueryPresetsSetVersionRetrieveQuery({
    presetsSetUuid,
    presetsSetVersionUuid,
  })
/** Query with the currently selected quality presets. */
const presetsQualityRetrieveRes = useSeqvarsQueryPresetsQualityRetrieveQuery({
  presetsSetVersionUuid,
  presetsQualityUuid,
})
/** Mutation for updating the quality presets. */
const qualityPresetsUpdate = useSeqvarsQueryPresetsQualityUpdateMutation()

/** Shortcut to the number of quality presets, used for rank. */
const maxRank = computed<number>(
  () =>
    presetsSetVersionRetrieveRes.data.value?.seqvarsquerypresetsquality_set
      .length ?? 0,
)

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Helper to apply a patch to the current `presetsQualityRetrieveRes.data.value`. */
const applyMutation = async (
  patch: Partial<SeqvarsQueryPresetsQuality>,
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
    presetsQualityRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value.status !==
      PresetSetVersionState.DRAFT
  ) {
    return
  } else {
    patch.rank = presetsQualityRetrieveRes.data.value.rank
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
      const others = version.seqvarsquerypresetsquality_set.filter((elem) => {
        if (elem.sodar_uuid === props.qualityPresets) {
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
          await qualityPresetsUpdate.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsquality: other.sodar_uuid,
            },
            body: {
              ...other,
              rank: newOtherRank,
            },
          })
        } catch (error) {
          emit('message', {
            text: `Failed to update other quality presets rank: ${error}`,
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
    await qualityPresetsUpdate.mutateAsync({
      path: {
        querypresetssetversion: props.presetSetVersion,
        querypresetsquality: presetsQualityRetrieveRes.data.value.sodar_uuid,
      },
      body: {
        ...presetsQualityRetrieveRes.data.value,
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
      text: `Failed to update quality presets: ${error}`,
      color: 'error',
    })
  }
}
</script>

<template>
  <h3>
    Quality Presets &raquo;{{
      presetsQualityRetrieveRes.data.value?.label ?? 'UNDEFINED'
    }}&laquo;
  </h3>

  <v-skeleton-loader
    v-if="presetsQualityRetrieveRes.status.value !== 'success'"
    type="article"
  />

  <v-form v-else ref="formRef">
    <v-checkbox
      :model-value="presetsQualityRetrieveRes.data.value?.filter_active"
      label="Filter Active"
      hide-details
      :disabled="readonly"
      @update:model-value="
        applyMutation({
          filter_active: !presetsQualityRetrieveRes.data.value?.filter_active,
        })
      "
    />

    <v-text-field
      :model-value="presetsQualityRetrieveRes.data.value?.label"
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
            presetsQualityRetrieveRes.data.value?.rank === undefined ||
            presetsQualityRetrieveRes.data.value?.rank <= 1
          "
          @click="applyMutation({}, -1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly ||
            presetsQualityRetrieveRes.data.value?.rank === undefined ||
            presetsQualityRetrieveRes.data.value?.rank >= maxRank
          "
          @click="applyMutation({}, 1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <div class="text-body-1 pb-3 pt-3">
      Clear the fields below to remove the filter threshold.
    </div>

    <v-number-input
      :model-value="presetsQualityRetrieveRes.data.value?.min_dp_het"
      label="Min DP Het: minimal depth required for heterozygous genotypes."
      clearable
      control-variant="stacked"
      :disabled="readonly"
      @update:model-value="(min_dp_het) => applyMutation({ min_dp_het })"
    />

    <v-number-input
      :model-value="presetsQualityRetrieveRes.data.value?.min_dp_hom"
      label="Min DP Hom: minimal depth required for homozygous genotypes."
      clearable
      control-variant="stacked"
      :disabled="readonly"
      @update:model-value="(min_dp_hom) => applyMutation({ min_dp_hom })"
    />

    <v-number-input
      :model-value="presetsQualityRetrieveRes.data.value?.min_ab_het"
      label="Min AB Het: minimal allelic balance for heterozygous genotypes."
      :step="0.01"
      clearable
      control-variant="stacked"
      :disabled="readonly"
      @update:model-value="(min_ab_het) => applyMutation({ min_ab_het })"
    />

    <v-number-input
      :model-value="presetsQualityRetrieveRes.data.value?.min_gq"
      label="Min GQ: minimal genotype quality required to pass."
      clearable
      control-variant="stacked"
      :disabled="readonly"
      @update:model-value="(min_gq) => applyMutation({ min_gq })"
    />

    <v-number-input
      :model-value="presetsQualityRetrieveRes.data.value?.min_ad"
      label="Min AD: minimal alternate read depth required to pass."
      clearable
      control-variant="stacked"
      :disabled="readonly"
      @update:model-value="(min_ad) => applyMutation({ min_ad })"
    />

    <v-number-input
      :model-value="presetsQualityRetrieveRes.data.value?.max_ad"
      label="Max AD: maximal alternate read depth allowed to pass."
      clearable
      control-variant="stacked"
      :disabled="readonly"
      @update:model-value="(max_ad) => applyMutation({ max_ad })"
    />
  </v-form>
</template>
