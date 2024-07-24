<script
  setup
  lang="ts"
  generic="
    PresetField extends keyof Query,
    SettingsField extends keyof Query,
    Preset extends { sodar_uuid: string; label: string } & Query[SettingsField]
  "
>
import { copy } from '@/varfish/helpers'

import Hr from '@/seqvars/components/ui/Hr.vue'
import Item from '@/seqvars/components/ui/Item.vue'
import { Query } from '@/seqvars/types'

const model = defineModel<Query>({ required: true })

const { presets, presetIdField, settingsField, matcher, onSelect } =
  defineProps<{
    presets: Preset[]
    settingsField: SettingsField
    presetIdField: PresetField
    matcher: (value: Query[SettingsField], preset: Preset) => boolean
    onSelect?: (preset: Preset) => void
  }>()

const setToPreset = (preset: Preset) => {
  if (onSelect) {
    onSelect(preset)
    return
  }
  model.value[presetIdField] = preset.sodar_uuid
  model.value[settingsField] = copy(preset)
}
</script>

<template>
  <div
    role="listbox"
    style="width: 100%; display: flex; flex-direction: column"
  >
    <Item
      v-for="preset in presets"
      :key="preset.sodar_uuid"
      :selected="preset.sodar_uuid === model[presetIdField]"
      :modified="!matcher(model[settingsField] as never, preset)"
      @click="() => setToPreset(preset)"
      @revert="() => setToPreset(preset)"
    >
      {{ preset.label }}
    </Item>
  </div>

  <Hr />
</template>
