<script lang="ts" setup>
import { onMounted, watch } from 'vue'

import SeqvarsFiltration from './views/SeqvarsFiltration.vue'
import { useCaseAnalysisStore } from './stores/caseAnalysis'
import { useSeqvarsPresetsStore } from './stores/presets'
import { useSeqvarsQueryStore } from './stores/query'
import { computed } from 'vue'

const appContext = JSON.parse(
  document
    .getElementById('sodar-ss-app-context')!
    .getAttribute('app-context') || '{}',
)

const props = defineProps<{ caseUuid: string }>()

const seqvarsPresetsStore = useSeqvarsPresetsStore()
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
          seqvarsPresetsStore.initialize(appContext.project.sodar_uuid),
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
          seqvarsPresetsStore.presetSets.values().next().value.sodar_uuid,
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
  [...seqvarsPresetsStore.presetSetVersions.values()].at(0),
)
</script>

<template>
  <SeqvarsFiltration v-if="presets" :presets="presets" />
</template>
