<script setup lang="ts">
import { computed } from 'vue'

import { RecessiveModeEnum } from '@varfish-org/varfish-api/lib'
import { Query } from '@/seqvars/types'

import { Affected, SexAssignedAtBirth } from './constants'
import InheritanceModeControls from './InheritanceModeControls.vue'
import RecessiveControls from './RecessiveControls.vue'
import SexAffectedIcon from './SexAffectedIcon'

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

const AFFECTED_STATUSES = [
  Affected.AFFECTED,
  Affected.UNAFFECTED,
  Affected.UNDEFINED,
]

const recessiveMode = computed<RecessiveModeEnum>({
  get: () => model.value.genotype.recessive_mode ?? 'disabled',
  set: (value) => {
    model.value.genotype.recessive_mode = value
  },
})

/** Items for the recessive mode VSelect. */
const RECESSIVE_MODE_ITEMS: { title: string; value: RecessiveModeEnum }[] = [
  {
    title: 'Disabled',
    value: 'disabled',
  },
  {
    title: 'Comp. Het. Recessive',
    value: 'comphet_recessive',
  },
  {
    title: 'Hom. Recessive',
    value: 'homozygous_recessive',
  },
  {
    title: 'Any Recessive',
    value: 'recessive',
  },
]
</script>

<template>
  <div style="width: 100%; display: flex; flex-direction: column; gap: 4px">
    <v-select
      v-model="recessiveMode"
      label="Recessive Mode"
      density="compact"
      variant="outlined"
      :hide-details="true"
      :items="RECESSIVE_MODE_ITEMS"
    />

    <div
      v-for="(choice, index) in model.genotype.sample_genotype_choices"
      :key="index"
      style="display: flex; flex-direction: row; align-items: start; gap: 4px"
    >
      <input
        :id="choice.sample"
        v-model="choice.enabled"
        type="checkbox"
        style="margin-top: 6px"
      />
      <div style="display: flex; flex-direction: column">
        <label
          :for="choice.sample"
          style="margin-bottom: 0; display: flex; align-items: center; gap: 8px"
          ><span>{{ choice.sample }}</span>

          <SexAffectedIcon
            :sex="
              choice.sample === 'father'
                ? SexAssignedAtBirth.MALE
                : choice.sample === 'mother'
                  ? SexAssignedAtBirth.FEMALE
                  : SexAssignedAtBirth.UNDEFINED
            "
            :affected="AFFECTED_STATUSES[(Math.random() * 3) | 0]"
          />
        </label>

        <InheritanceModeControls
          v-if="recessiveMode === 'disabled'"
          v-model="model.genotype.sample_genotype_choices![index]"
          :legend="choice.sample"
        />
        <RecessiveControls
          v-else-if="model.genotype.sample_genotype_choices"
          v-model="model.genotype.sample_genotype_choices!"
          :index="index"
          :sample-name="choice.sample"
        />
      </div>
    </div>
  </div>
</template>
