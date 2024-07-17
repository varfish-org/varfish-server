<script setup lang="ts">
import { defineEmits, ref } from 'vue'

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
import { type RecessiveModeEnum } from '@varfish-org/varfish-api/lib'

const { pedigreeMembers } = defineProps<{ pedigreeMembers: PedigreeMember[] }>()

const model = defineModel<GenotypeModel>({ required: true })
defineEmits(['changePreset'])

const recessiveMode = ref<RecessiveModeEnum>('disabled')
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

      <v-select model="recessiveMode" label="Recessive mode" :items="['disabled', 'comphet_recessive', 'homozygous_recessive', 'recessive']" />

      <Hr />

      <div v-if="recessiveMode === 'disabled'">
        <h4>Genotype Pattern Mode</h4>
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
      <div v-else>
        <h4>Recessive Mode</h4>
        <div
          v-for="(member, index) in pedigreeMembers"
          :key="index"
          style="display: flex; flex-direction: row; align-items: start; gap: 4px"
        >
          <div>
            <label>{{ member.name }}</label>
            <v-checkbox label="recessive index" /><!-- exactly one individual index -->
            <v-checkbox label="parent" /><!-- at most two are parent, parent/index rule mutually exclusive -->
          </div>
        </div>
      </div>
    </div>
  </CollapsibleGroup>
</template>
