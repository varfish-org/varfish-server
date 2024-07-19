<script setup lang="ts">
import { SeqvarsQueryPresetsFrequency } from '@varfish-org/varfish-api/lib'

import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Hr from '@/seqvars/components/Hr.vue'
import Item from '@/seqvars/components/Item.vue'
import ModifiedIcon from '@/seqvars/components/ModifiedIcon.vue'
import { Query } from '@/seqvars/types'
import { copy } from '@/varfish/helpers'

import FrequencyControls from './FrequencyControls.vue'
import { matchesFrequencyPreset } from './utils'

const { presets } = defineProps<{ presets: SeqvarsQueryPresetsFrequency[] }>()
const model = defineModel<Query>({
  required: true,
})
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
            <ModifiedIcon
              v-if="
                preset.sodar_uuid === model.frequencypresets &&
                !matchesFrequencyPreset(model.frequency, preset)
              " /></template
        ></Item>
      </div>

      <Hr />

      <FrequencyControls v-model="model.frequency" />
    </div>
  </CollapsibleGroup>
</template>
