<script setup lang="ts">
/**
 * This component allows to edit the per-sample quality presets.
 *
 * The component is passed the current seqvar query for editing and updates
 * it via TanStack Query.
 */
import {
  SeqvarsQueryDetails,
  SeqvarsSampleQualityFilterPydanticList,
} from '@varfish-org/varfish-api/lib'

import { useSeqvarQueryUpdateMutation } from '@/seqvars/queries/seqvarQuery'

import { _Unpacked } from '../PresetsEditor/lib'
import AbbrHint from './ui/AbbrHint.vue'
import Input from './ui/Input.vue'
import SmallText from './ui/SmallText.vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** The query that is to be edited. */
    modelValue: SeqvarsQueryDetails
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

/** Type for per-sample quality settings. */
type SeqvarsSampleQualityFilter =
  _Unpacked<SeqvarsSampleQualityFilterPydanticList>

/** Quality filter fields. */
const FILTER_FIELDS = [
  { key: 'min_dp_het', label: 'max DP hom.' },
  { key: 'min_dp_hom', label: 'min DP hom.' },
  { key: 'min_ab_het', label: 'mit AB' },
  { key: 'min_gq', label: 'min GQ' },
  { key: 'min_ad', label: 'min AD' },
  { key: 'max_ad', label: 'max AD' },
] as const

/**
 * Mutation for updating a seqvar query.
 *
 * This is done via TanStack Query which uses optimistic updates for quick
 * reflection in the UI.
 */
const seqvarQueryUpdate = useSeqvarQueryUpdateMutation()

/**
 * Helper to apply a patch to the current `props.modelValue` for a specific
 * sample index.
 */
const applyMutation = async (
  index: number,
  quality: SeqvarsSampleQualityFilter,
) => {
  const newData = {
    ...props.modelValue,
    settings: {
      ...props.modelValue.settings,
      quality: {
        ...props.modelValue.settings.quality,
        sample_quality_filters: [
          ...(props.modelValue.settings.quality.sample_quality_filters ?? []),
        ],
      },
    },
  }
  newData.settings.quality.sample_quality_filters[index] = quality

  // Apply update via TanStack query; will use optimistic updates for quick
  // reflection in the UI.
  await seqvarQueryUpdate.mutateAsync({
    body: newData,
    path: {
      session: props.modelValue.session,
      query: props.modelValue.sodar_uuid,
    },
  })
}
</script>

<template>
  <div
    style="
      width: fit-content;
      display: grid;
      grid-template-columns: 1fr auto auto auto auto auto auto;
      gap: 4px;
    "
  >
    <SmallText style="grid-column: 2">
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Minimal depth of coverage for het. genotypes."
      >
        min<br />DP het
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Minimal depth of coverage for hom. genotypes."
      >
        min<br />DP hom
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Minimal allelic balance for het. genotypes."
      >
        min<br />AB
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Minimal genotype quality for any genotype."
      >
        min<br />GQ
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Minimal number of reads showing alternate allele for any genotype."
      >
        min<br />AD
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Maximal number of reads showing alternate allele for any genotype (useful for parents in de novo search)."
      >
        max<br />AD
      </AbbrHint>
    </SmallText>

    <template
      v-for="(item, index) in modelValue.settings.quality
        .sample_quality_filters"
      :key="index"
    >
      <v-checkbox
        :model-value="item.filter_active"
        color="primary"
        :label="item.sample"
        class="d-flex align-items-center ga-4"
        style="grid-column: span 7"
        density="compact"
        @change="
          async () =>
            await applyMutation(index, {
              ...item,
              filter_active: !item.filter_active,
            })
        "
      />

      <fieldset style="display: contents">
        <div style="width: 25px"></div>
        <Input
          v-for="{ key, label } in FILTER_FIELDS"
          :key="key"
          :model-value="item[key]"
          :aria-label="label"
          :style="
            key === 'min_dp_het'
              ? { 'grid-column': 2, width: '32px' }
              : { width: '32px' }
          "
          @update:model-value="
            async (value) => {
              await applyMutation(index, {
                ...item,
                [key]: value === null ? null : Number(value),
              })
            }
          "
        />
      </fieldset>
    </template>
  </div>
</template>
