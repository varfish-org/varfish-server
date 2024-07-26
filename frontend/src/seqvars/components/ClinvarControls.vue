<script setup lang="ts">
import { Query } from '@/seqvars/types'
import { ClinvarGermlineAggregateDescriptionList } from '@varfish-org/varfish-api/lib'

import { toggleArrayElement } from './utils'

const model = defineModel<Query>({ required: true })

const GERMLINE_FIELDS = [
  'pathogenic',
  'likely_pathogenic',
  'uncertain_significance',
  'likely_benign',
  'benign',
] satisfies ClinvarGermlineAggregateDescriptionList[number][]

const capitalize = (s: string) => s && s[0].toUpperCase() + s.slice(1)
</script>

<template>
  <v-checkbox
    v-model="model.clinvar.clinvar_presence_required"
    label="Require ClinVar assessment"
    :hide-details="true"
    density="compact"
  />

  <div style="padding-left: 16px">
    <v-checkbox
      v-for="field in GERMLINE_FIELDS"
      :key="field"
      :label="capitalize(field.split('_').join(' '))"
      :model-value="
        model.clinvar.clinvar_germline_aggregate_description?.includes(field)
      "
      :hide-details="true"
      density="compact"
      @update:model-value="
        toggleArrayElement(
          model.clinvar.clinvar_germline_aggregate_description,
          field,
        )
      "
    />

    <v-checkbox
      v-model="model.clinvar.allow_conflicting_interpretations"
      label="Allow conflicting interpretations"
      :hide-details="true"
      density="compact"
      style="margin-top: 8px"
    />
  </div>
</template>
