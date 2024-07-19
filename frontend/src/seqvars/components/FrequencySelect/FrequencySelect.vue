<script setup lang="ts">
import { SeqvarsQueryPresetsFrequency } from '@varfish-org/varfish-api/lib'

import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Hr from '@/seqvars/components/Hr.vue'
import Item from '@/seqvars/components/Item.vue'
import ItemButton from '@/seqvars/components/ItemButton.vue'
import ModifiedIcon from '@/seqvars/components/ModifiedIcon.vue'
import { Query } from '@/seqvars/types'
import { copy } from '@/varfish/helpers'

import FrequencyControls from './FrequencyControls.vue'
import { matchesFrequencyPreset } from './utils'

const { presets } = defineProps<{ presets: SeqvarsQueryPresetsFrequency[] }>()
const model = defineModel<Query>({
  required: true,
})

const isSelectedAndModified = (preset: SeqvarsQueryPresetsFrequency) =>
  preset.sodar_uuid === model.value.frequencypresets &&
  !matchesFrequencyPreset(model.value.frequency, preset)
</script>

<template>
  <CollapsibleGroup title="Frequency">
    <div style="width: 100%; display: flex; flex-direction: column; gap: 4px">
      <div
        role="listbox"
        style="width: 100%; display: flex; flex-direction: column"
      >
        <Item
          v-for="preset in presets"
          :key="preset.sodar_uuid"
          :selected="preset.sodar_uuid === model.frequencypresets"
          @click="
            () => {
              model.frequencypresets = preset.sodar_uuid
              model.frequency = copy(preset)
            }
          "
        >
          <template #default>{{ preset.label }}</template>
          <template #extra>
            <ModifiedIcon v-if="isSelectedAndModified(preset)" />
            <ItemButton
              v-if="isSelectedAndModified(preset)"
              @click="
                () => {
                  model.frequencypresets = preset.sodar_uuid
                  model.frequency = copy(preset)
                }
              "
              ><i-fluent-arrow-undo-20-regular style="font-size: 0.9em"
            /></ItemButton> </template
        ></Item>
      </div>

      <Hr />

      <FrequencyControls v-model="model.frequency" />
    </div>
  </CollapsibleGroup>
</template>
