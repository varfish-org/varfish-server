<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { useCaseListStore } from '@/cases/stores/caseList'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { useVariantQueryStore } from '@/variants/stores/variantQuery'
import { QueryPresetsClient } from '@/variants/api/queryPresetsClient'
import UiToggleMaxButton from '@/varfish/components/UiToggleMaxButton/UiToggleMaxButton.vue'

const router = useRouter()

const caseListStore = useCaseListStore()
const caseDetailsStore = useCaseDetailsStore()
const variantQueryStore = useVariantQueryStore()

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  formVisible: Boolean,
})

const emit = defineEmits(['editQueryPresetsClick', 'toggleForm'])

/** Whether the preset set is loading. */
const presetSetLoading = ref(false)
/** The current preset set (if caseDetailsStore.caseObj.presetset !== null / factory presets). */
const presetSetLabel = ref(null)
const presetSource = ref(null)
/** Watch change of current case's preset set and load label if necessary. */
const updatePresetSetLoading = async () => {
  let uuid
  if (
    !caseDetailsStore?.caseObj?.presetset &&
    variantQueryStore?.defaultPresetSetUuid === undefined
  ) {
    presetSource.value = 'Factory Defaults'
    return // short circuit in case of factory defaults
  } else {
    if (caseDetailsStore?.caseObj?.presetset) {
      uuid = caseDetailsStore.caseObj.presetset
      presetSource.value = 'Individual Case Setting'
    } else if (variantQueryStore?.defaultPresetSetUuid !== undefined) {
      uuid = variantQueryStore.defaultPresetSetUuid
      presetSource.value = 'Project Default Setting'
    }
  }
  const queryPresetsClient = new QueryPresetsClient(caseListStore.csrfToken)
  presetSetLoading.value = true
  await queryPresetsClient
    .retrievePresetSet(uuid)
    .then((presetSet) => {
      presetSetLabel.value = presetSet.label
    })
    .catch((err) => {
      console.error('Problem retrieving preset set', err)
    })
    .finally(() => {
      presetSetLoading.value = false
    })
}
watch(
  () => caseDetailsStore?.caseObj?.presetset,
  async (newValue, _oldValue) => {
    if (!newValue) {
      return // short circuit in case of factory defaults
    }
    await updatePresetSetLoading()
  },
)
onMounted(() => {
  updatePresetSetLoading()
})
</script>

<template>
  <div class="row sodar-pr-content-title pb-1">
    <!-- TODO buttons from sodar core -->
    <h2 class="sodar-pr-content-title">
      Filter Variants for Case
      <small class="text-muted">{{ caseDetailsStore.caseObj.name }}</small>
      <small class="badge badge-primary ml-2" style="font-size: 50%">
        {{ caseDetailsStore.caseObj.release }}
      </small>

      <a
        id="sodar-pr-btn-copy-uuid"
        role="submit"
        class="btn btn-link mr-2 sodar-pr-btn-title sodar-pr-btn-copy-uuid sodar-copy-btn"
        data-clipboard-text="{{ caseDetailsStore.caseUuid }}"
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
            name: 'case-detail-overview',
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
            name: 'svs-filter',
            params: { case: caseDetailsStore.caseObj.sodar_uuid },
          })
        "
      >
        <i-mdi-filter-variant />
        Filter SVs
      </a>
      <UiToggleMaxButton />
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
          <template
            v-if="
              caseDetailsStore.caseObj?.presetset ||
              variantQueryStore?.defaultPresetSetUuid
            "
          >
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
