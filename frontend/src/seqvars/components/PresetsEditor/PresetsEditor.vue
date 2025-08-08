<script setup lang="ts">
import QueryPresetsEditor from '@/seqvars/components/PresetsEditor/QueryPresetsEditor.vue'
import QueryPresetsSelect from '@/seqvars/components/PresetsEditor/QueryPresetsSelect.vue'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

/** Props used in this component. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** UUID of the current preset set. */
  presetSet?: string
  /** UUID of the current presest set version. */
  presetSetVersion?: string
}>()

/** This component's events. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits<{
  message: [message: SnackbarMessage]
}>()
</script>

<template>
  <h2>Query Presets</h2>

  <v-alert type="warning" variant="tonal" closable>
    <v-alert-title> Upcoming Feature... </v-alert-title>
    Note that the presets here are only for the upcoming "Version 2" interface.
    Most likely, you are looking for the non-V2 query presets.
  </v-alert>

  <QueryPresetsSelect
    :project-uuid="projectUuid"
    :preset-set="presetSet"
    :preset-set-version="presetSetVersion"
    @message="emit('message', $event)"
  />

  <QueryPresetsEditor
    :project-uuid="projectUuid"
    :preset-set="presetSet"
    :preset-set-version="presetSetVersion"
    @message="emit('message', $event)"
  />
</template>
