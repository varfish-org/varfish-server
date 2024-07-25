<script lang="ts" setup>
import { onMounted, watch } from 'vue'

import SeqvarsFiltration from './views/SeqvarsFiltration.vue'
import { useCaseAnalysisStore } from './stores/caseAnalysis'
import { useSeqvarPresetsStore } from './stores/presets'
import { useSeqvarsQueryStore } from './stores/query'
import { computed } from 'vue'

const appContext = JSON.parse(
  document
    .getElementById('sodar-ss-app-context')!
    .getAttribute('app-context') || '{}',
)

const props = defineProps<{ caseUuid: string }>()

const seqvarPresetsStore = useSeqvarPresetsStore()
const caseAnalysisStore = useCaseAnalysisStore()
const seqvarsQueryStore = useSeqvarsQueryStore()

const refreshStores = async () => {
  if (
    appContext?.csrf_token &&
    appContext?.project?.sodar_uuid &&
    props?.caseUuid
  ) {
    await Promise.all([
      (async () => {
        await Promise.all([
          seqvarPresetsStore.initialize(appContext.project.sodar_uuid),
          caseAnalysisStore.initialize(
            appContext.project.sodar_uuid,
            props.caseUuid,
          ),
        ])
        await seqvarsQueryStore.initialize(
          appContext.project.sodar_uuid,
          props.caseUuid,
          caseAnalysisStore.currentAnalysis!.sodar_uuid,
          caseAnalysisStore.currentSession!.sodar_uuid,
          seqvarPresetsStore.presetSets.values().next().value.sodar_uuid,
        )
      })(),
    ])
  }
}

onMounted(() => {
  refreshStores()
})

watch(
  () => props.caseUuid,
  () => refreshStores(),
)

const presets = computed(() =>
  [...seqvarPresetsStore.presetSetVersions.values()].at(0),
)
</script>

<template>
  <SeqvarsFiltration v-if="presets" :presets="presets" />
</template>
