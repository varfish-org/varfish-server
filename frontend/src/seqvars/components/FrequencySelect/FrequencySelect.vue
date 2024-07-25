<script setup lang="ts">
import { SeqvarsQueryPresetsFrequency } from '@varfish-org/varfish-api/lib'

import CollapsibleGroup from '../ui/CollapsibleGroup.vue'
import PresetSelect from '../ui/PresetSelect.vue'
import { Query } from '@/seqvars/types'

import FrequencyControls from './FrequencyControls.vue'
import { matchesFrequencyPreset } from './utils'

const { presets } = defineProps<{ presets: SeqvarsQueryPresetsFrequency[] }>()
const model = defineModel<Query>({ required: true })
</script>

<template>
  <CollapsibleGroup
    title="Frequency"
    :summary="
      presets.find((p) => p.sodar_uuid === model.frequencypresets)?.label
    "
  >
    <div style="width: 100%; display: flex; flex-direction: column; gap: 4px">
      <PresetSelect
        v-model="model"
        :presets="presets"
        preset-id-field="frequencypresets"
        settings-field="frequency"
        :matcher="matchesFrequencyPreset"
      />

      <FrequencyControls v-model="model.frequency" />
    </div>
  </CollapsibleGroup>
</template>
