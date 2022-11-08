<script setup>
import { ref, watch } from 'vue'

import { useCasesStore } from '@cases/stores/cases.js'
import { useCaseDetailsStore } from '@cases/stores/case-details.js'

import queryPresetsApi from '@variants/api/queryPresets.js'

/** Define emits. */
const emit = defineEmits(['editQueryPresetsClick'])

const casesStore = useCasesStore()
const caseDetailsStore = useCaseDetailsStore()

/** Whether the preset set is loading. */
const presetSetLoading = ref(false)
/** The current preset set (if caseDetailsStore.caseObj.presetset !== null / factory presets). */
const presetSetLabel = ref(null)
/** Watch change of current case's preset set and load label if necessary. */
watch(
  () => caseDetailsStore?.caseObj?.presetset,
  async (newValue, _oldValue) => {
    if (!newValue) {
      return // short circuit in case of factory defaults
    }
    const csrfToken = casesStore.appContext.csrf_token
    presetSetLoading.value = true
    try {
      const presetSet = await queryPresetsApi.retrievePresetSet(
        csrfToken,
        newValue
      )
      presetSetLabel.value = presetSet.label
    } catch (err) {
      console.error('Problem retrieving preset set', err)
    } finally {
      presetSetLoading.value = false
    }
  }
)
</script>

<template>
  <div
    class="card mb-3 flex-grow-1"
    style="overflow-y: auto !important; max-height: 300px"
  >
    <div class="row card-header p-2 pl-2">
      <h5 class="col-auto ml-0 mr-0 mb-0">
        <i-mdi-filter />
        Query Related
      </h5>
      <div class="btn-group ml-auto">
        <a
          class="btn btn-sm btn-primary"
          href="#"
          @click.prevent="emit('editQueryPresetsClick')"
        >
          <i-mdi-square-edit-outline />
          Edit Query Presets
        </a>
      </div>
    </div>
    <ul class="list-group list-group-flush" v-if="caseDetailsStore.caseObj">
      <li class="list-group-item pl-0">
        <div class="row">
          <span class="col-3 text-nowrap font-weight-bold">
            Query Presets
          </span>
          <span v-if="caseDetailsStore.caseObj.presetset" class="col-3">
            <template v-if="presetSetLoading">
              <i-fa-solid-circle-notch v-if="presetSetLoading" class="spin" />
            </template>
            <template v-else>
              {{ presetSetLabel }}
            </template>
          </span>
          <span v-else class="col-3 text-muted font-italic">
            Factory Defaults
          </span>
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
