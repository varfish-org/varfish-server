<script setup lang="ts">
import {
  ClinvarGermlineAggregateDescriptionChoice,
  SeqvarsQueryDetails,
} from '@varfish-org/varfish-api/lib'
import { computed } from 'vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)
const model = defineModel<SeqvarsQueryDetails>({ required: true })

type Choices =
  | ClinvarGermlineAggregateDescriptionChoice
  | 'allow_conflicting_interpretations'

const GERMLINE_FIELDS = [
  'pathogenic',
  'likely_pathogenic',
  'uncertain_significance',
  'likely_benign',
  'benign',
] satisfies ClinvarGermlineAggregateDescriptionChoice[]

const choiceValue = computed<Choices[]>({
  get: () => {
    const result: Choices[] = []
    if (model.value.settings.clinvar.allow_conflicting_interpretations) {
      result.push('allow_conflicting_interpretations')
    }
    for (const field of GERMLINE_FIELDS) {
      if (
        model.value.settings.clinvar.clinvar_germline_aggregate_description?.includes(
          field,
        )
      ) {
        result.push(field)
      }
    }
    return result
  },
  set: (value: Choices[]) => {
    model.value.settings.clinvar.allow_conflicting_interpretations =
      value.includes('allow_conflicting_interpretations')
    model.value.settings.clinvar.clinvar_germline_aggregate_description =
      value.filter(
        (v) => v !== 'allow_conflicting_interpretations',
      ) as ClinvarGermlineAggregateDescriptionChoice[]
  },
})
</script>

<template>
  <div class="mt-2">
    <v-checkbox
      v-model="model.settings.clinvar.clinvar_presence_required"
      color="primary"
      label="Require ClinVar assessment"
      hide-details
      density="compact"
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
