<script setup lang="ts">
import { defineEmits } from 'vue'

import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import {
  matchesGenotypePreset,
  getGenotypeValueFromPreset,
} from '@/seqvars/components/GenotypeSelect/utils'
import Hr from '@/seqvars/components/Hr.vue'
import Item from '@/seqvars/components/Item.vue'
import ModifiedIcon from '@/seqvars/components/ModifiedIcon.vue'
import InheritanceModeControls from './InheritanceModeControls.vue'
import SexAffectedIcon from './SexAffectedIcon'
import {
  GENOTYPE_PRESETS,
  GenotypeModel,
  GenotypePresetKey,
  PedigreeMember,
} from './constants'

const { pedigreeMembers } = defineProps<{ pedigreeMembers: PedigreeMember[] }>()

const model = defineModel<GenotypeModel>({ required: true })
defineEmits(['changePreset'])
</script>

<template>
  <CollapsibleGroup title="Genotype">
    <div style="width: 100%; display: flex; flex-direction: column; gap: 4px">
      <div
        role="listbox"
        style="width: 100%; display: flex; flex-direction: column"
      >
        <Item
          v-for="key in Object.keys(GENOTYPE_PRESETS)"
          :key="key"
          :selected="model.preset == key"
          @click="
            () => {
              model = getGenotypeValueFromPreset(key as GenotypePresetKey)
            }
          "
        >
          <template #default>{{
            key == 'ANY' ? 'any mode' : key.toLowerCase().split('_').join(' ')
          }}</template>
          <template #extra>
            <ModifiedIcon
              v-if="model.preset == key && !matchesGenotypePreset(model, key)"
            />
          </template>
        </Item>
      </div>

      <Hr />

      <div
        v-for="(member, index) in pedigreeMembers"
        :key="index"
        style="display: flex; flex-direction: row; align-items: start; gap: 4px"
      >
        <input
          :id="member.name"
          v-model="model.value[member.name].checked"
          type="checkbox"
          style="margin-top: 6px"
        />
        <div style="display: flex; flex-direction: column">
          <label
            :for="member.name"
            style="
              margin-bottom: 0;
              display: flex;
              align-items: center;
              gap: 8px;
            "
            ><span>{{ member.name }}</span>

            <SexAffectedIcon
              :sex="member.sexAssignedAtBirth"
              :affected="member.affected"
            />
          </label>
          <InheritanceModeControls v-model="model.value[member.name].mode" />
        </div>
      </div>
    </div>
  </CollapsibleGroup>
</template>
