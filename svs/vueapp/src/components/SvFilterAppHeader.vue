<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { useSvFilterStore } from '@svs/stores/filterSvs.js'
import { useCasesStore } from '@cases/stores/cases.js'
import { useCaseDetailsStore } from '@cases/stores/case-details.js'
// TODO: change to sv presets
import queryPresetsApi from '@variants/api/queryPresets.js'

const router = useRouter()

const casesStore = useCasesStore()
const caseDetailsStore = useCaseDetailsStore()
const svFilterStore = useSvFilterStore()

const props = defineProps({
  formVisible: Boolean,
})

const emit = defineEmits(['toggleForm'])

/** Whether the preset set is loading. */
const presetSetLoading = ref(false)
/** The current preset set (if svFilterStore.caseObj.presetset !== null / factory presets). */
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
        newValue,
      )
      presetSetLabel.value = presetSet.label
    } catch (err) {
      console.error('Problem retrieving preset set', err)
    } finally {
      presetSetLoading.value = false
    }
  },
)
</script>

<template>
  <div class="row sodar-pr-content-title pb-1">
    <!-- TODO buttons from sodar core -->
    <h2 class="sodar-pr-content-title">
      Filter SVs for Case
      <small class="text-muted">{{ svFilterStore.caseObj.name }}</small>
      <small class="badge badge-primary ml-2" style="font-size: 50%">
        {{ svFilterStore.caseObj.release }}
      </small>

      <a
        role="submit"
        class="btn btn-link mr-2 sodar-pr-btn-title sodar-pr-btn-copy-uuid sodar-copy-btn"
        id="sodar-pr-btn-copy-uuid"
        data-clipboard-text="{{ svFilterStore.caseUuid }}"
        title="Copy UUID to clipboard"
        data-toggle="tooltip"
        data-placement="top"
      >
        <i-fa-solid-clipboard class="text-muted" />
      </a>
    </h2>

    <a
      href="#"
      class="btn btn-sm btn-secondary"
      @click.prevent="emit('toggleForm')"
    >
      <i-mdi-button-cursor />
      <span v-if="formVisible">hide form</span>
      <span v-if="!formVisible">show form</span>
    </a>

    <div class="ml-auto btn-group">
      <a
        class="btn btn-secondary"
        @click.prevent="
          router.push({
            name: 'case-detail',
            params: { case: caseDetailsStore.caseObj.sodar_uuid },
          })
        "
      >
        <i-mdi-arrow-left-circle />
        Back to Case
      </a>

      <a
        class="btn btn-primary"
        @click.prevent="
          router.push({
            name: 'variants-filter',
            params: { case: caseDetailsStore.caseObj.sodar_uuid },
          })
        "
      >
        <i-mdi-filter />
        Filter Variants
      </a>
      <a
        type="button"
        class="btn btn-secondary dropdown-toggle"
        data-toggle="dropdown"
      >
        <i-mdi-cog />
      </a>
      <div class="dropdown-menu">
        <a
          class="dropdown-item disabled"
          href="#"
          @click.prevent="emit('editQueryPresetsClick')"
        >
          Query Presets:
          <template v-if="svFilterStore.caseObj?.presetset">
            <template v-if="presetSetLoading">
              <i-fa-solid-circle-notch v-if="presetSetLoading" class="spin" />
            </template>
            <template v-else>
              {{ presetSetLabel }}
            </template>
          </template>
          <template v-else> Factory Defaults </template>
        </a>
      </div>
    </div>
    <!-- TODO case filter buttons as component -->
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
