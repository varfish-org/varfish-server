<script setup lang="ts">
import { computed, defineEmits } from 'vue'

import {
  RecessiveModeEnum,
  SeqvarsGenotypePresetChoice,
} from '@varfish-org/varfish-api/lib'
import { copy } from '@/varfish/helpers'

import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Hr from '@/seqvars/components/Hr.vue'
import Item from '@/seqvars/components/Item.vue'
import { Query } from '@/seqvars/types'

import { Affected, GENOTYPE_PRESETS, SexAssignedAtBirth } from './constants'
import InheritanceModeControls from './InheritanceModeControls.vue'
import RecessiveControls from './RecessiveControls.vue'
import SexAffectedIcon from './SexAffectedIcon'
import { getGenotypeSettingsFromPreset, matchesGenotypePreset } from './utils'

const model = defineModel<Query>({ required: true })
defineEmits(['changePreset'])

const affectedStatuses = [
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

const setToPreset = (key: SeqvarsGenotypePresetChoice) => {
  model.value.genotype = copy(getGenotypeSettingsFromPreset(key))
  model.value.genotypepresets = { choice: key }
}
</script>

<template>
  <CollapsibleGroup title="Genotype">
    <div style="width: 100%; display: flex; flex-direction: column; gap: 4px">
      <div
        role="listbox"
        style="width: 100%; display: flex; flex-direction: column"
      >
        <Item
          v-for="key in Object.keys(
            GENOTYPE_PRESETS,
          ) as SeqvarsGenotypePresetChoice[]"
          :key="key"
          :selected="model.genotypepresets?.choice == key"
          :modified="!matchesGenotypePreset(model.genotype, key)"
          @click="() => setToPreset(key)"
          @revert="() => setToPreset(key)"
        >
          {{
            key == 'any' ? 'any mode' : key.toLowerCase().split('_').join(' ')
          }}
        </Item>
      </div>

      <Hr />

      <v-select
        v-model="recessiveMode"
        label="recessive"
        density="compact"
        :hide-details="true"
        :items="
          [
            'disabled',
            'comphet_recessive',
            'homozygous_recessive',
            'recessive',
          ].map((i) => ({ title: i.split('_').join(' '), value: i }))
        "
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
            style="
              margin-bottom: 0;
              display: flex;
              align-items: center;
              gap: 8px;
            "
            ><span>{{ choice.sample }}</span>

            <SexAffectedIcon
              :sex="
                choice.sample == 'father'
                  ? SexAssignedAtBirth.MALE
                  : choice.sample == 'mother'
                    ? SexAssignedAtBirth.FEMALE
                    : SexAssignedAtBirth.UNDEFINED
              "
              :affected="affectedStatuses[(Math.random() * 3) | 0]"
            />
          </label>

          <InheritanceModeControls
            v-if="recessiveMode == 'disabled'"
            v-model="model.genotype.sample_genotype_choices![index]"
          />
          <RecessiveControls
            v-else-if="model.genotype.sample_genotype_choices"
            v-model="model.genotype.sample_genotype_choices!"
            :index="index"
          />
        </div>
      </div>
    </div>
  </CollapsibleGroup>
</template>
