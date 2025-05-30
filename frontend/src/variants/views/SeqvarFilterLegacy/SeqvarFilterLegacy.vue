<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import TheNavBar from '@/cases/components/TheNavBar/TheNavBar.vue'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { useCaseListStore } from '@/cases/stores/caseList'
import { useProjectStore } from '@/cases/stores/project/store'
import SeqvarDetails from '@/seqvars/components/SeqvarDetails/SeqvarDetails.vue'
import { useCtxStore } from '@/varfish/stores/ctx'
import { QueryPresetsClient } from '@/variants/api/queryPresetsClient'
import FilterApp from '@/variants/components/FilterApp.vue'
import { useVariantQueryStore } from '@/variants/stores/variantQuery'

const props = defineProps<{
  /** The project UUID. */
  projectUuid: string
  /** The case UUID. */
  caseUuid?: string
}>()

const caseListStore = useCaseListStore()
const projectStore = useProjectStore()

/** Whether to hide the navigation bar; component state. */
const navbarShown = ref<boolean>(true)
/** Whether to hide the variant details pane; component state. */
const detailsShown = ref<boolean>(false)
/** Whether to open the details in details sheet; component state. */
const detailsInSheet = ref<boolean>(false)

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

const router = useRouter()

const ctxStore = useCtxStore()
const caseDetailsStore = useCaseDetailsStore()
const variantQueryStore = useVariantQueryStore()

const filtrationComplexityMode = computed(() => {
  switch (variantQueryStore.filtrationComplexityMode) {
    case 'simple':
      return '1'
    case 'normal':
      return '2'
    case 'advanced':
      return '3'
    case 'dev':
      return '4'
  }
  return '1'
})

const toggleFiltrationComplexityMode = () => {
  switch (variantQueryStore.filtrationComplexityMode) {
    case 'simple':
      variantQueryStore.filtrationComplexityMode = 'normal'
      break
    case 'normal':
      variantQueryStore.filtrationComplexityMode = 'advanced'
      break
    case 'advanced':
      variantQueryStore.filtrationComplexityMode = 'dev'
      break
    case 'dev':
      variantQueryStore.filtrationComplexityMode = 'simple'
      break
  }
}

const resultRowUuid = ref<string | null>(null)
const selectedSection = ref<string | null>(null)

const showDetails = async (event: {
  smallvariantresultrow: string
  selectedSection: string
}) => {
  // @ts-ignore
  variantQueryStore.lastPosition = document.querySelector('div#app').scrollTop
  if (detailsInSheet.value) {
    detailsShown.value = true
    resultRowUuid.value = event.smallvariantresultrow
    selectedSection.value = event.selectedSection ?? null
  } else {
    router.push({
      name: 'seqvar-details',
      params: {
        row: event.smallvariantresultrow,
        selectedSection: event.selectedSection ?? null,
      },
    })
  }
}

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
    (variantQueryStore?.defaultPresetSetUuid === undefined ||
      variantQueryStore?.defaultPresetSetUuid === null)
  ) {
    presetSetUuid.value = null
    presetSource.value = 'Factory Defaults'
    return // short circuit in case of factory defaults
  } else {
    if (caseDetailsStore?.caseObj?.presetset) {
      presetSetUuid.value = caseDetailsStore.caseObj.presetset
      presetSource.value = 'Individual Case Setting'
    } else if (
      variantQueryStore?.defaultPresetSetUuid !== undefined &&
      variantQueryStore?.defaultPresetSetUuid !== null
    ) {
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
  <v-app id="seqvar-filter-legacy">
    <v-main>
      <TheAppBar
        v-model:show-left-panel="navbarShown"
        v-model:show-right-panel="detailsShown"
        :show-left-panel-button="true"
        :show-right-panel-button="true"
        :title="
          caseDetailsStore.caseObj?.name
            ? `VarFish - ${caseDetailsStore.caseObj?.name}`
            : undefined
        "
      />

      <TheNavBar :navbar-shown="navbarShown">
        <v-list-item
          prepend-icon="mdi-arrow-left"
          :to="{
            name: 'case-detail-overview',
            params: { project: projectUuid, case: caseUuid },
          }"
        >
          <template v-if="navbarShown"> Back to Case </template>
        </v-list-item>
        <v-list-subheader v-if="navbarShown" class="text-uppercase">
          Variant Analysis
        </v-list-subheader>
        <v-list-item
          :class="{ 'pt-3 mt-1 border-t-thin': !navbarShown }"
          prepend-icon="mdi-filter-variant"
          :to="{
            name: 'svs-filter',
            params: { case: caseUuid },
          }"
        >
          <template v-if="navbarShown"> Go To SV Filtration </template>
        </v-list-item>
        <v-list-subheader v-if="navbarShown" class="text-uppercase">
          <template v-if="navbarShown"> Analysis Info </template>
        </v-list-subheader>
        <v-list-item
          :class="{ 'pt-3 mt-1 border-t-thin': !navbarShown }"
          prepend-icon="mdi-button-cursor"
          @click="filterFormVisible = !filterFormVisible"
        >
          <template v-if="navbarShown"> Toggle Form </template>
        </v-list-item>
        <v-list-item
          :prepend-icon="`mdi-numeric-${filtrationComplexityMode}-box-multiple`"
          @click="toggleFiltrationComplexityMode()"
        >
          <template v-if="navbarShown"> Toggle Complexity </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-card-text-outline"
          @click="logsVisible = !logsVisible"
        >
          <template v-if="navbarShown"> Toggle Logs </template>
        </v-list-item>
        <!-- <v-list-item
          :prepend-icon="`mdi-window-${detailsInSheet ? 'restore' : 'maximize'}`"
          @click="detailsInSheet = !detailsInSheet"
        >
          <template v-if="navbarShown"> Toggle Details Sheet </template>
        </v-list-item> -->
        <v-list-item v-if="!presetSetUuid" prepend-icon="mdi-factory" link>
          <template v-if="navbarShown"> Filter: Defaults </template>
        </v-list-item>
        <v-list-item
          v-else
          prepend-icon="mdi-filter-settings"
          lines="two"
          :title="presetSetLabel ?? undefined"
          :subtitle="presetSource ?? undefined"
          :to="{
            name: 'case-list-query-presets-non-factory',
            params: {
              project: projectUuid,
              presetSet: presetSetUuid!,
            },
          }"
        />
      </TheNavBar>
      <FilterApp
        v-model:filter-form-visible="filterFormVisible"
        v-model:query-logs-visible="logsVisible"
        :project-uuid="props.projectUuid"
        :case-uuid="props.caseUuid"
        @variant-selected="showDetails"
      />

      <SeqvarDetails
        v-if="resultRowUuid"
        v-model:show-sheet="detailsShown"
        :project-uuid="props.projectUuid"
        :result-row-uuid="resultRowUuid ?? ''"
      />
    </v-main>
  </v-app>
</template>
