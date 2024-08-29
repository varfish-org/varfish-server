<script setup lang="ts">
/**
 * This component allows to edit the effects-based filtering settings.
 *
 * The component is passed the current seqvar query for editing and updates
 * it via TanStack Query.
 */
import {
  SeqvarsQueryDetails,
  SeqvarsQuerySettingsConsequenceRequest,
  SeqvarsTranscriptTypeChoiceList,
  SeqvarsVariantTypeChoiceList,
} from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'

import { useSeqvarQueryUpdateMutation } from '@/seqvars/queries/seqvarQuery'

import {
  CODING_CONSEQUENCES,
  ConsequenceChoice,
  NON_CODING_CONSEQUENCES,
  OFF_EXOMES_CONSEQUENCES,
  SPLICING_CONSEQUENCES,
} from '../PresetsEditor/lib'
import { toggleArrayElement } from '../utils'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'

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

/** Mapping from variant type to their label. */
const VARIANT_TYPES = {
  snv: 'SNV',
  indel: 'indel',
  mnv: 'MNV',
  complex_substitution: 'complex substitution',
} satisfies Record<SeqvarsVariantTypeChoiceList[number], string>

/** Mapping from transcript types to their label. */
const TRANSCRIPT_TYPES = {
  coding: 'coding',
  non_coding: 'non-coding',
} satisfies Record<SeqvarsTranscriptTypeChoiceList[number], string>

/** Two-level mapping of all settings and  */
const CUSTOMIZATION = {
  Coding: CODING_CONSEQUENCES,
  'Off-Exome': OFF_EXOMES_CONSEQUENCES,
  'Non-coding': NON_CODING_CONSEQUENCES,
  Splicing: SPLICING_CONSEQUENCES,
} satisfies Record<string, ConsequenceChoice[]>

/** Whether the details are opend. */
const detailsOpen = ref<boolean>(false)

/**
 * Mutation for updating a seqvar query.
 *
 * This is done via TanStack Query which uses optimistic updates for quick
 * reflection in the UI.
 */
const seqvarQueryUpdate = useSeqvarQueryUpdateMutation()

/** Helper to apply a patch to the current `props.modelValue`. */
const applyMutation = async (
  consequence: SeqvarsQuerySettingsConsequenceRequest,
) => {
  const newData = {
    ...props.modelValue,
    settings: {
      ...props.modelValue.settings,
      consequence: {
        ...props.modelValue.settings.consequence,
        ...consequence,
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

/** Helper to update the maximal distance to exons. */
const maxExonDistance = computed<number | null | undefined>({
  get: () => props.modelValue.settings.consequence.max_distance_to_exon,
  set(value: string | number | null | undefined) {
    applyMutation({
      max_distance_to_exon:
        value === null || value === undefined || value === ''
          ? null
          : Number(value),
    })
  },
})
</script>

<template>
  <div class="d-flex flex-column ga-2">
    <div class="mt-2">
      <div class="text-body-2">Max distance to next exon</div>
      <v-row class="align-center" justify="start" no-gutters>
        <!-- Button Group -->
        <v-col cols="auto" class="pt-0">
          <v-btn-group density="compact" color="primary" divided>
            <v-btn
              class="px-0"
              :variant="maxExonDistance === null ? 'flat' : 'outlined'"
              @click="maxExonDistance = null"
            >
              any
            </v-btn>
            <v-btn
              class="px-0"
              :variant="maxExonDistance == 20 ? 'flat' : 'outlined'"
              @click="maxExonDistance = 20"
            >
              20
            </v-btn>
            <v-btn
              class="px-0"
              :variant="maxExonDistance == 100 ? 'flat' : 'outlined'"
              @click="maxExonDistance = 100"
            >
              100
            </v-btn>
          </v-btn-group>
        </v-col>

        <!-- Text Field -->
        <v-col cols="auto" class="pl-3 pt-0">
          <v-text-field
            v-model="maxExonDistance"
            density="compact"
            variant="outlined"
            hide-details
            class="exon-distance-text-field"
          />
        </v-col>
      </v-row>
    </div>

    <div>
      <div class="text-body-2">Variant Type</div>
      <v-checkbox
        v-for="(label, key) in VARIANT_TYPES"
        :key="key"
        :label="label"
        :hide-details="true"
        color="primary"
        density="compact"
        :model-value="
          modelValue.settings.consequence.variant_types?.includes(key)
        "
        @update:model-value="
          async () => {
            await applyMutation({
              variant_types: toggleArrayElement(
                modelValue.settings.consequence.variant_types,
                key,
              ),
            })
          }
        "
      />
    </div>

    <div>
      <div class="text-body-2">Transcript Type</div>
      <v-checkbox
        v-for="(label, key) in TRANSCRIPT_TYPES"
        :key="key"
        :label="label"
        :hide-details="true"
        color="primary"
        density="compact"
        :model-value="
          modelValue.settings.consequence.transcript_types?.includes(key)
        "
        @update:model-value="
          async () => {
            await applyMutation({
              transcript_types: toggleArrayElement(
                modelValue.settings.consequence.transcript_types,
                key,
              ),
            })
          }
        "
      />
    </div>

    <CollapsibleGroup v-model:is-open="detailsOpen" title="Customize effects">
      <div style="display: flex; flex-direction: column; gap: 8px">
        <div v-for="(choices, title) in CUSTOMIZATION">
          <div class="text-body-2">{{ title }}</div>

          <v-checkbox
            v-for="{ label, key } in choices"
            :key="key"
            :label="label"
            color="primary"
            :hide-details="true"
            density="compact"
            :model-value="
              modelValue.settings.consequence.variant_consequences?.includes(
                key,
              )
            "
            @update:model-value="
              async () =>
                await applyMutation({
                  variant_consequences: toggleArrayElement(
                    modelValue.settings.consequence.variant_consequences,
                    key,
                  ),
                })
            "
          />
        </div>
      </div>
    </CollapsibleGroup>
  </div>
</template>

<style>
.exon-distance-text-field .v-field__input {
  min-height: 24px !important;
  padding-block-start: 6px !important;
  padding-block-end: 6px !important;
  padding-bottom: 6px !important;
  padding-top: 6px !important;
  padding-left: 6px !important;
  padding-right: 6px !important;
  max-width: 60px;
}
</style>
