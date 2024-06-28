<script setup lang="ts">
import { ref, watch } from 'vue'

import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Item from '@/seqvars/components/Item.vue'
import InheritanceModeControls from './InheritanceModeControls.vue'
import SexAffectedIcon from './SexAffectedIcon'
import { GENOTYPE_LABELS } from './constants'
import { PedigreeMember } from './types'

const { pedigreeMembers } = defineProps<{ pedigreeMembers: PedigreeMember[] }>()

const membersInheritanceMode = ref(pedigreeMembers.map(() => new Set()))

watch(pedigreeMembers, () => {
  membersInheritanceMode.value = pedigreeMembers.map(
    (_, i) => membersInheritanceMode.value.at(i) ?? new Set(),
  )
})
</script>

<template>
  <CollapsibleGroup title="Genotype">
    <div style="width: 100%; display: flex; flex-direction: column; gap: 16px">
      <div style="width: 100%; display: flex; flex-direction: column">
        <Item
          v-for="[key, label] in Object.entries(GENOTYPE_LABELS)"
          :key="key"
          >{{ label }}</Item
        >
      </div>

      <div
        class="bg-inactive-ui-element"
        style="margin: 4px 0; width: 100%; height: 1px"
      ></div>

      <div
        v-for="(member, index) in pedigreeMembers"
        :key="member.name"
        style="display: flex; flex-direction: row; align-items: start; gap: 4px"
      >
        <input :id="member.name" type="checkbox" style="margin-top: 6px" />
        <div style="display: flex; flex-direction: column">
          <label
            :for="member.name"
            style="
              margin-bottom: 4px;
              display: flex;
              align-items: center;
              gap: 4px;
            "
            ><span>{{ member.name }}</span>

            <SexAffectedIcon
              :sex="member.sexAssignedAtBirth"
              :affected="member.affected"
            />
          </label>
          <InheritanceModeControls v-model="membersInheritanceMode[index]" />
        </div>
      </div>
    </div>
  </CollapsibleGroup>
</template>
