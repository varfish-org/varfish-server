<script setup lang="ts">
/**
 * This component allows to edit the ClinVar filter settings.
 *
 * The component is passed the current seqvar query for editing and updates
 * it via TanStack Query.
 *
 * To simplify the UI, we are using a single `VBtnToggle` group for selecting
 * both the ClinVar levels and allowing conflicts.  We use `ComputedRef`
 * to enable this single-array--based interface.
 */
import {
  ClinvarGermlineAggregateDescriptionChoice,
  SeqvarsQueryDetails,
  SeqvarsQuerySettingsClinvarRequest,
} from '@varfish-org/varfish-api/lib'
import { computed } from 'vue'

import { useSeqvarQueryUpdateMutation } from '@/seqvars/queries/seqvarQuery'

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

/** Type for the array-only--based interface. */
type Choices =
  | ClinvarGermlineAggregateDescriptionChoice
  | 'allow_conflicting_interpretations'

const GERMLINE_FIELDS = [
  'pathogenic',
  'likely_pathogenic',
  'uncertain_significance',
  'likely_benign',
  'benign',
] as const

/**
 * Mutation for updating a seqvar query.
 *
 * This is done via TanStack Query which uses optimistic updates for quick
 * reflection in the UI.
 */
const seqvarQueryUpdate = useSeqvarQueryUpdateMutation()

/** Helper to apply a patch to the current `props.modelValue`. */
const applyMutation = async (clinvar: SeqvarsQuerySettingsClinvarRequest) => {
  const newData = {
    ...props.modelValue,
    settings: {
      ...props.modelValue.settings,
      clinvar: {
        ...props.modelValue.settings.clinvar,
        ...clinvar,
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

/** Helper to provide array-only--based interface to the clinvar settings. */
const choiceValue = computed<Choices[]>({
  get: () => {
    const result: Choices[] = []
    if (props.modelValue.settings.clinvar.allow_conflicting_interpretations) {
      result.push('allow_conflicting_interpretations')
    }
    for (const field of GERMLINE_FIELDS) {
      if (
        props.modelValue.settings.clinvar.clinvar_germline_aggregate_description?.includes(
          field,
        )
      ) {
        result.push(field)
      }
    }
    return result
  },
  set: (value: Choices[]) => {
    applyMutation({
      allow_conflicting_interpretations: value.includes(
        'allow_conflicting_interpretations',
      ),
      clinvar_germline_aggregate_description: value.filter(
        (v) => v !== 'allow_conflicting_interpretations',
      ) as ClinvarGermlineAggregateDescriptionChoice[],
    })
  },
})
</script>

<template>
  <div class="mt-2">
    <v-checkbox
      :model-value="modelValue.settings.clinvar.clinvar_presence_required"
      color="primary"
      label="Require ClinVar assessment"
      hide-details
      density="compact"
      @update:model-value="
        applyMutation({ clinvar_presence_required: $event ?? undefined })
      "
    />
    <div class="text-body-2 mt-2 mb-1 ml-1">
      Annotate with ClinVar assessments
    </div>
    <v-btn-toggle
      v-model="choiceValue"
      multiple
      color="primary"
      variant="outlined"
      divided
      density="default"
      class="ml-1 mb-2"
    >
      <v-btn icon title="Pathogenic" value="pathogenic" class="pa-0"> P </v-btn>
      <v-btn icon title="Likely pathogenic" value="likely_pathogenic">
        LP
      </v-btn>
      <v-btn icon title="Uncertain significance" value="uncertain_significance">
        US
      </v-btn>
      <v-btn icon title="Likely benign" value="likely_benign"> LB </v-btn>
      <v-btn icon title="Benign" value="benign"> B </v-btn>
      <v-btn
        icon="mdi-flash"
        title="Allow conflicting interpretations"
        value="allow_conflicting_interpretations"
      />
    </v-btn-toggle>
  </div>
</template>
