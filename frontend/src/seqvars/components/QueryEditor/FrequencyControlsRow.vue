<script setup lang="ts">
/**
 * This component provides a row in the frequency editor table.
 *
 * It takes the current seqvar query and information on the database to
 * display the editor for.  All updating is done using TanStack Query.
 *
 * The main complexity of this component is the handling of the different
 * database types and their respective counts.
 */
import {
  SeqvarsQueryDetails,
  SeqvarsQuerySettingsFrequencyRequest,
} from '@varfish-org/varfish-api/lib'

import { useSeqvarQueryUpdateMutation } from '@/seqvars/queries/seqvarQuery'

import Input from '../QueryEditor/ui/Input.vue'
import { FrequencyDb, ValueOf } from './lib'

/** This component's props. */
const props = defineProps<{
  /** The query that is to be edited. */
  modelValue: SeqvarsQueryDetails
  /** Key into the `modelValue.settings.frequency` object. */
  db: FrequencyDb
  /** Label for the database. */
  label: string
  /** Number of samples in database. */
  size?: number
}>()

/** Values of mitochondrial counts. */
const MITOCHONDRIAL_ATTRS = ['max_hom', 'max_het'] as const
/** Values of nuclear counts. */
const NUCLEAR_ATTRS = ['max_hom', 'max_het', 'max_hemi'] as const

/**
 * Mutation for updating a seqvar query.
 *
 * This is done via TanStack Query which uses optimistic updates for quick
 * reflection in the UI.
 */
const seqvarQueryUpdate = useSeqvarQueryUpdateMutation()

/** Helper to apply a patch to the current `model.value`. */
const applyMutation = async (
  freqs: ValueOf<SeqvarsQuerySettingsFrequencyRequest>,
) => {
  const newData = {
    ...props.modelValue,
    settings: {
      ...props.modelValue.settings,
      frequency: {
        ...props.modelValue.settings.frequency,
        [props.db]: {
          ...props.modelValue.settings.frequency[props.db],
          ...freqs,
        },
      },
    },
  }

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
  <input
    :id="label"
    :checked="modelValue.settings.frequency[db]!.enabled ?? false"
    type="checkbox"
    @change="
      async () => {
        applyMutation({
          ...modelValue.settings.frequency[db],
          enabled: !modelValue.settings.frequency[db]!.enabled,
        })
      }
    "
  />
  <label
    :for="label"
    style="
      grid-column: span 4;
      margin-bottom: 0;
      display: flex;
      align-items: center;
      gap: 4px;
    "
  >
    {{ label }}
    <span v-if="size !== undefined" style="color: #808080"> {{ size }}k </span>
  </label>

  <Input
    v-if="db !== 'inhouse'"
    :model-value="
      // frequency editor in percent, stored as fractions
      modelValue.settings.frequency[db]!.max_af === null ||
      modelValue.settings.frequency[db]!.max_af === undefined
        ? null
        : modelValue.settings.frequency[db]!.max_af! * 100.0
    "
    type="number"
    aria-label="frequency"
    style="grid-column: 2; margin-right: 8px; width: 56px"
    :step="0.1"
    @update:model-value="
      // frequency editor in percent, stored as fractions
      async (value) => {
        applyMutation({
          ...modelValue.settings.frequency[db],
          max_af: value === null ? null : Number(value) / 100.0,
        })
      }
    "
  >
    <template #after> % </template>
  </Input>
  <Input
    v-else
    :model-value="modelValue.settings.frequency[db]!.max_carriers"
    type="number"
    aria-label="carriers"
    style="grid-column: 2; margin-right: 8px; width: 56px"
    :step="1"
    @update:model-value="
      async (value) => {
        applyMutation({
          ...modelValue.settings.frequency[db],
          max_carriers: value === null ? null : Number(value),
        })
      }
    "
  >
  </Input>

  <template v-if="db === 'gnomad_mtdna' || db === 'helixmtdb'">
    <template v-for="attr in MITOCHONDRIAL_ATTRS" :key="attr">
      <Input
        :model-value="modelValue.settings.frequency[db]![attr]"
        :aria-label="attr"
        type="number"
        style="width: 40px"
        :step="1"
        @update:model-value="
          async (value) => {
            applyMutation({
              ...modelValue.settings.frequency[db]!,
              [attr]: value === null ? null : Number(value),
            })
          }
        "
      />
    </template>
    <span />
  </template>
  <template v-else>
    <template v-for="attr in NUCLEAR_ATTRS" :key="attr">
      <Input
        :model-value="modelValue.settings.frequency[db]![attr]"
        :aria-label="attr"
        type="number"
        style="width: 40px"
        :step="1"
        @update:model-value="
          async (value) => {
            applyMutation({
              ...modelValue.settings.frequency[db]!,
              [attr]: value === null ? null : Number(value),
            })
          }
        "
      />
    </template>
  </template>
</template>
