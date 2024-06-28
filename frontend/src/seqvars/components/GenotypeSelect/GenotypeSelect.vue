<script setup lang="ts">
import { ref } from 'vue'

import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import InheritanceModeControls from './InheritanceModeControls.vue'
import { Affected, PedigreeMember, SexAssignedAtBirth } from './types'
import { watch } from 'vue'

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
        <Item>de novo</Item>
        <Item>dominant</Item>
        <Item>affected caries</Item>
        <Item>any mode</Item>
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

            <i-bi-diamond
              v-if="
                member.sexAssignedAtBirth == SexAssignedAtBirth.UNDEFINED &&
                member.affected == Affected.UNAFFECTED
              "
            />
            <i-bi-diamond-fill
              v-if="
                member.sexAssignedAtBirth == SexAssignedAtBirth.UNDEFINED &&
                member.affected == Affected.AFFECTED
              "
            />

            <i-bi-circle
              v-if="
                member.sexAssignedAtBirth == SexAssignedAtBirth.FEMALE &&
                member.affected == Affected.UNAFFECTED
              "
            />
            <i-bi-circle-fill
              v-if="
                member.sexAssignedAtBirth == SexAssignedAtBirth.FEMALE &&
                member.affected == Affected.AFFECTED
              "
            />

            <i-bi-square
              v-if="
                member.sexAssignedAtBirth == SexAssignedAtBirth.MALE &&
                member.affected == Affected.UNAFFECTED
              "
            />
            <i-bi-square-fill
              v-if="
                member.sexAssignedAtBirth == SexAssignedAtBirth.MALE &&
                member.affected == Affected.AFFECTED
              "
            />
          </label>
          <InheritanceModeControls v-model="membersInheritanceMode[index]" />
        </div>
      </div>
    </div>
  </CollapsibleGroup>
</template>
