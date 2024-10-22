<script setup lang="ts">
import {
  SeqvarsQueryDetails,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'

import { PedigreeObj } from '@/cases/stores/caseDetails'

import { GROUPS, matchesQualityPreset } from './groups'
import Item from './ui/Item.vue'

type Preset =
  SeqvarsQueryPresetsSetVersionDetails[(typeof GROUPS)[number]['presetSetKey']][0]

defineProps<{
  pedigree: PedigreeObj
  presetsDetails: SeqvarsQueryPresetsSetVersionDetails
  group: (typeof GROUPS)[number]
  preset?: Preset
  query: SeqvarsQueryDetails
}>()
defineEmits<{ revert: [preset: Preset] }>()
</script>

<template>
  <Item
    v-if="preset"
    :modified="
      preset.sodar_uuid === query.settings[group.queryPresetKey] &&
      !(group.id === 'quality'
        ? matchesQualityPreset(pedigree, presetsDetails, query.settings)
        : group.matchesPreset(presetsDetails, query.settings))
    "
    @revert="() => preset && $emit('revert', preset)"
  >
    {{ preset?.label }}
  </Item>
</template>
