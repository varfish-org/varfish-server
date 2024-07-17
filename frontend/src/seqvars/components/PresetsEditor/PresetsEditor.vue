<script setup lang="ts">
import QueryPresetsSelect from '@/seqvars/components/PresetsEditor/QueryPresetsSelect.vue'
import QueryPresetsEditor from '@/seqvars/components/PresetsEditor/QueryPresetsEditor.vue'

/** Props used in this component. */
const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** UUID of the current preset set. */
  presetSet?: string
  /** UUID of the current presest set version. */
  presetSetVersion?: string
}>()
</script>

<template>
  <h2>Query Presets</h2>
  <QueryPresetsSelect
    :project-uuid="projectUuid"
    :preset-set="presetSet"
    :preset-set-version="presetSetVersion"
    class="mt-3"
  />
  <QueryPresetsEditor
    :project-uuid="projectUuid"
    :preset-set="presetSet"
    :preset-set-version="presetSetVersion"
    class="mt-3"
  />
</template>
