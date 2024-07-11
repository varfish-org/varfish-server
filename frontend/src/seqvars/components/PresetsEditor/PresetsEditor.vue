<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'

import QueryPresetsSelect from '@/seqvars/components/PresetsEditor/QueryPresetSelect.vue'
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'

/** Props used in this component. */
const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** Identifier of the current preset set. */
  presetSet?: string
}>()

/** Store with the presets. */
const seqvarsPresetsStore = useSeqvarsPresetsStore()
</script>

<template>
  <h2>Query Presets</h2>

  <QueryPresetsSelect :project-uuid="projectUuid" :preset-set="presetSet" />
</template>
