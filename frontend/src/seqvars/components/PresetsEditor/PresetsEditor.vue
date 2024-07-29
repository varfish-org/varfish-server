<script setup lang="ts">
import QueryPresetsSelect from '@/seqvars/components/PresetsEditor/QueryPresetsSelect.vue'
import QueryPresetsEditor from '@/seqvars/components/PresetsEditor/QueryPresetsEditor.vue'
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
  <QueryPresetsSelect
    :project-uuid="projectUuid"
    :preset-set="presetSet"
    :preset-set-version="presetSetVersion"
    class="mt-3"
    @message="emit('message', $event)"
  />
  <QueryPresetsEditor
    :project-uuid="projectUuid"
    :preset-set="presetSet"
    :preset-set-version="presetSetVersion"
    class="mt-3"
    @message="emit('message', $event)"
  />
</template>
