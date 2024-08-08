<script setup lang="ts">
import { watch, onMounted, ref } from 'vue'

import CaseListTable from '@/cases/components/CaseListTable/CaseListTable.vue'
import CaseListQc from '@/cases/components/CaseListQc/CaseListQc.vue'
import { Tab } from './types'
import QueryPresets from '@/variants/components/QueryPresets.vue'
import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import TheNavBar from '@/cases/components/TheNavBar/TheNavBar.vue'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

import { useCaseListStore } from '@/cases/stores/caseList'
import { useProjectStore } from '@/cases/stores/project/store'

const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** Identifier of the current tab. */
  currentTab?: Tab
  /** Identifier of the current preset set. */
  presetSet?: string
}>()

const caseListStore = useCaseListStore()
const projectStore = useProjectStore()

// Whether to hide the navigation bar; component state.
const navbarHidden = ref<boolean>(false)
/** Messages to display in VSnackbarQueue; component state. */
const messages = ref<SnackbarMessage[]>([])

/** Event handler for queueing message in VSnackbarQueue. */
const queueMessage = (message: SnackbarMessage) => {
  messages.value.push(message)
}

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
</script>

<template>
  <v-app id="case-list">
    <v-main>
      <TheAppBar
        :show-left-panel-button="true"
        :show-right-panel-button="false"
        v-model:hide-left-panel="navbarHidden"
      />
      <TheNavBar :navbar-hidden="navbarHidden">
        <v-list-item
          prepend-icon="mdi-arrow-left"
          :href="`/project/${projectStore.projectUuid}`"
        >
          <template v-if="!navbarHidden"> Back to Project </template>
        </v-list-item>
        <v-list-subheader v-if="!navbarHidden" class="text-uppercase">
          Project Overview
        </v-list-subheader>
        <v-list-item
          :class="{ 'pt-3 mt-1 border-t-thin': navbarHidden }"
          prepend-icon="mdi-format-list-bulleted-square"
          :to="{
            name: 'case-list',
            params: { project: projectStore.projectUuid },
          }"
        >
          <template v-if="!navbarHidden"> Case List </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-chart-multiple"
          :to="{
            name: 'case-list-qc',
            params: { project: projectStore.projectUuid },
          }"
        >
          <template v-if="!navbarHidden"> Quality Control </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-filter-settings"
          :to="{
            name: 'case-list-query-presets',
            params: { project: projectStore.projectUuid },
          }"
        >
          <template v-if="!navbarHidden"> Query Presets </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-numeric-2-box-multiple-outline"
          :to="{
            name: 'seqvars-query-presets',
            params: { project: projectStore.projectUuid },
          }"
        >
          <template v-if="!navbarHidden"> Query Presets (V2) </template>
        </v-list-item>
      </TheNavBar>
      <div class="pa-3">
        <div v-if="props.currentTab === Tab.CASE_LIST">
          <CaseListTable :project-uuid="projectUuid" @message="queueMessage" />
        </div>
        <div v-else-if="props.currentTab === Tab.QUALITY_CONTROL">
          <CaseListQc />
        </div>
        <div v-else-if="props.currentTab === Tab.QUERY_PRESETS">
          <QueryPresets :preset-set="presetSet" />
        </div>
        <div v-else>
          <v-alert type="error">Unknown tab: {{ props.currentTab }}</v-alert>
        </div>
      </div>
    </v-main>
    <v-snackbar-queue
      v-model="messages"
      timer="5000"
      close-on-content-click
    ></v-snackbar-queue>
  </v-app>
</template>
