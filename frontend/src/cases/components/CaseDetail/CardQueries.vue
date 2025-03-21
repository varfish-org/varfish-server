<script setup>
import { onMounted, ref, watch } from 'vue'

import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { useCaseListStore } from '@/cases/stores/caseList'
import { QueryPresetsClient } from '@/variants/api/queryPresetsClient'

/** Define emits. */
const emit = defineEmits(['editQueryPresetsClick'])

const caseListStore = useCaseListStore()
const caseDetailsStore = useCaseDetailsStore()

/** Whether the preset set is loading. */
const presetSetLoading = ref(false)
/** The current preset set (if caseDetailsStore.caseObj.presetset !== null / factory presets). */
const presetSetLabel = ref(null)

const loadCasePresetSetLabel = async (presetSetUuid) => {
  if (!presetSetUuid) {
    presetSetLabel.value = null
    return
  }
  const queryPresetsClient = new QueryPresetsClient(caseListStore.csrfToken)
  presetSetLoading.value = true
  try {
    const presetSet = await queryPresetsClient.retrievePresetSet(presetSetUuid)
    presetSetLabel.value = presetSet.label
  } catch (err) {
    console.error('Problem retrieving preset set', err)
  } finally {
    presetSetLoading.value = false
  }
}

/** Watch change of current case's preset set and load label if necessary. */
watch(
  () => caseDetailsStore?.caseObj?.presetset,
  async (newPreset, _oldPreset) => {
    await loadCasePresetSetLabel(newPreset)
  },
)

onMounted(async () => {
  await loadCasePresetSetLabel(caseDetailsStore?.caseObj?.presetset)
})
</script>

<template>
  <div
    class="card mb-3 flex-grow-1"
    style="overflow-y: auto !important; max-height: 300px"
  >
    <h5 class="card-header p-2">
      <i-mdi-filter />
      Query Related
      <div class="btn-group float-right">
        <a
          class="btn btn-sm btn-primary"
          href="#"
          @click.prevent="emit('editQueryPresetsClick')"
        >
          <i-mdi-square-edit-outline />
          Edit Query Presets
        </a>
      </div>
    </h5>
    <ul v-if="caseDetailsStore?.caseObj" class="list-group list-group-flush">
      <li class="list-group-item pl-3">
        <div class="row">
          <span class="col-3 text-nowrap font-weight-bold">
            Query Presets
          </span>
          <template v-if="presetSetLoading">
            <i-fa-solid-circle-notch v-if="presetSetLoading" class="spin" />
          </template>
          <div v-else class="col-9">
            <template v-if="presetSetLabel">
              {{ presetSetLabel }}
            </template>
            <template v-else-if="caseDetailsStore?.projectDefaultPresetSet">
              Project Default
              <span class="text-muted"
                >({{ caseDetailsStore.projectDefaultPresetSet.label }})</span
              >
            </template>
            <span v-else class="text-muted font-italic">
              Factory Defaults
            </span>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.spin {
  animation-name: spin;
  animation-duration: 2000ms;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
