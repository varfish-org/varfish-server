<script setup lang="ts">
import { Query } from '@/seqvars/types'
import { ClinvarGermlineAggregateDescriptionChoiceList } from '@varfish-org/varfish-api/lib'

import { toggleArrayElement } from '../utils'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)
const model = defineModel<Query>({ required: true })

const GERMLINE_FIELDS = [
  'pathogenic',
  'likely_pathogenic',
  'uncertain_significance',
  'likely_benign',
  'benign',
] satisfies ClinvarGermlineAggregateDescriptionChoiceList[number][]

const capitalize = (s: string) => s && s[0].toUpperCase() + s.slice(1)
</script>

<template>
  <v-checkbox
    v-model="model.clinvar.clinvar_presence_required"
    label="Require ClinVar assessment"
    :hide-details="true"
    density="compact"
  />

  <v-row class="d-flex align-center flex-row my-2">
    <v-col cols="auto">
      <v-btn-toggle
        multiple
        color="primary"
        variant="outlined"
        divided
        density="default"
        v-model="model.clinvar.clinvar_germline_aggregate_description"
      >
        <v-btn icon title="Pathogenic" value="pathogenic"> P </v-btn>
        <v-btn icon title="Likely pathogenic" value="likely_pathogenic">
          LP
        </v-btn>
        <v-btn
          icon
          title="Uncertain significance"
          value="uncertain_significance"
        >
          VUS
        </v-btn>
        <v-btn icon title="Likely benign" value="likely_benign"> LB </v-btn>
        <v-btn icon title="Benign" value="benign"> B </v-btn>
      </v-btn-toggle>
    </v-col>
    <v-col>
      <v-btn-toggle
        color="primary"
        variant="outlined"
        divided
        density="default"
        v-model="model.clinvar.allow_conflicting_interpretations"
      >
      <v-btn
        icon="mdi-head-flash"
        title="Allow conflicts"
        :value="true"
        @click.prevent.stop="
          // sic! need to convert undefined to false
          model.clinvar.allow_conflicting_interpretations =
            !!model.clinvar.allow_conflicting_interpretations
        "
      />
      </v-btn-toggle>
    </v-col>
  </v-row>
</template>
