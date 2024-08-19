<script setup lang="ts">
import { SeqvarsQueryPresetsSetVersionDetails } from '@varfish-org/varfish-api/lib'
import { Query } from '@/seqvars/types'

import { GROUPS, matchesQualityPreset } from './groups'
import Item from './ui/Item.vue'
import { PedigreeObj } from '@/cases/stores/caseDetails'

type Preset =
  SeqvarsQueryPresetsSetVersionDetails[(typeof GROUPS)[number]['presetSetKey']][0]

defineProps<{
  pedigree: PedigreeObj
  presetsDetails: SeqvarsQueryPresetsSetVersionDetails
  group: (typeof GROUPS)[number]
  preset?: Preset
  query: Query
}>()
defineEmits<{ revert: [preset: Preset] }>()
</script>

<template>
  <Item
    v-if="preset"
    :modified="
      preset.sodar_uuid == query[group.queryPresetKey] &&
      !(group.id == 'quality'
        ? matchesQualityPreset(pedigree, presetsDetails, query)
        : group.matchesPreset(presetsDetails, query))
    "
    @revert="() => preset && $emit('revert', preset)"
  >
    {{ preset?.label }}
  </Item>
</template>
