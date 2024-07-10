<script setup lang="ts">
import { watch, onMounted, ref } from 'vue'

import FilterApp from '@/variants/components/FilterApp.vue'
import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import TheNavBar from '@/cases/components/TheNavBar/TheNavBar.vue'
import { QueryPresetsClient } from '@/variants/api/queryPresetsClient'

import { useCaseListStore } from '@/cases/stores/caseList'
import { useProjectStore } from '@/cases/stores/project/store'
import { useCtxStore } from '@/varfish/stores/ctx'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { useVariantQueryStore } from '@/variants/stores/variantQuery'

const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** The case UUID. */
  caseUuid?: string
}>()

const caseListStore = useCaseListStore()
const projectStore = useProjectStore()

// Whether to hide the navigation bar; component state.
const navbarHidden = ref<boolean>(false)

const filterFormVisible = ref<boolean>(true)
const logsVisible = ref<boolean>(false)

// Initialize case list store on mount.
onMounted(() => {
  caseListStore.initialize(props.projectUuid)
  projectStore.initialize(props.projectUuid)
})
// Re-initialize case list store when the project changes.
watch(
  () => props.projectUuid,
  (newValue) => {
    caseListStore.initialize(newValue)
    projectStore.initialize(newValue)
  },
)

const ctxStore = useCtxStore()
const caseDetailsStore = useCaseDetailsStore()
const variantQueryStore = useVariantQueryStore()


/** Whether the preset set is loading. */
const presetSetLoading = ref<boolean>(false)
/** The current preset set (if caseDetailsStore.caseObj.presetset !== null / factory presets). */
const presetSetLabel = ref<string | null>(null)
const presetSource = ref<string | null>(null)
const presetSetUuid = ref<string | null>(null)
/** Watch change of current case's preset set and load label if necessary. */
const updatePresetSetLoading = async () => {
  if (
    !caseDetailsStore?.caseObj?.presetset &&
    (variantQueryStore?.defaultPresetSetUuid === undefined || variantQueryStore?.defaultPresetSetUuid === null)
  ) {
    presetSetUuid.value = null
    presetSource.value = 'Factory Defaults'
    return // short circuit in case of factory defaults
  } else {
    if (caseDetailsStore?.caseObj?.presetset) {
      presetSetUuid.value = caseDetailsStore.caseObj.presetset
      presetSource.value = 'Individual Case Setting'
    } else if (variantQueryStore?.defaultPresetSetUuid !== undefined && variantQueryStore?.defaultPresetSetUuid !== null) {
      presetSetUuid.value = variantQueryStore.defaultPresetSetUuid
      presetSource.value = 'Project Default Setting'
    }
  }
  const queryPresetsClient = new QueryPresetsClient(ctxStore.csrfToken)
  presetSetLoading.value = true
  await queryPresetsClient
    .retrievePresetSet(presetSetUuid.value!)
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
  <v-app id="case-list">
    <TheAppBar v-model:navbar-hidden="navbarHidden" />
    <TheNavBar :navbar-hidden="navbarHidden">
      <v-list-item
        prepend-icon="mdi-arrow-left"
        :to="{
          name: 'case-detail-overview',
          params: { project: projectUuid, case: caseUuid },
        }"
      >
        Back to Case
      </v-list-item>
      <v-list-subheader class="text-uppercase">
        Variant Analysis
      </v-list-subheader>
      <v-list-item
        prepend-icon="mdi-filter-variant"
        :to="{
          name: 'svs-filter',
          params: { case: caseUuid },
        }"
      >
        Filter SVs
      </v-list-item>
      <v-list-subheader class="text-uppercase">
        Analysis Info
      </v-list-subheader>
      <v-list-item prepend-icon="mdi-button-cursor" @click="filterFormVisible = !filterFormVisible">
        Toggle Form
      </v-list-item>
      <v-list-item prepend-icon="mdi-card-text-outline" @click="logsVisible = !logsVisible">
        Toggle Logs
      </v-list-item>
      <v-list-item prepend-icon="mdi-factory" link v-if="!presetSetUuid">
        Filter: Defaults
      </v-list-item>
      <v-list-item prepend-icon="mdi-filter-settings" v-else lines="two" :title="presetSetLabel ?? undefined" :subtitle="presetSource ?? undefined" :to="{
        name: 'case-list-query-presets-non-factory',
        params: {
          project: projectUuid,
          presetSet: presetSetUuid!,
        }
      }" />
    </TheNavBar>
    <v-main>
      <FilterApp :project-uuid="props.projectUuid" :case-uuid="props.caseUuid" v-model:filter-form-visible="filterFormVisible" v-model:query-logs-visible="logsVisible" />
    </v-main>
  </v-app>
</template>
