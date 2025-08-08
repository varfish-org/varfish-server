<script setup lang="ts">
import { VueQueryDevtools } from '@tanstack/vue-query-devtools'
import { ref } from 'vue'
import { onMounted } from 'vue'

import CaseListQc from '@/cases/components/CaseListQc/CaseListQc.vue'
import CaseListTable from '@/cases/components/CaseListTable/CaseListTable.vue'
import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import TheNavBar from '@/cases/components/TheNavBar/TheNavBar.vue'
import { useCaseListStore } from '@/cases/stores/caseList'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'
import QueryPresets from '@/variants/components/QueryPresets.vue'

import { Tab } from './types'

const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** Identifier of the current tab. */
  currentTab?: Tab
  /** Identifier of the current preset set. */
  presetSet?: string
}>()

const caseListStore = useCaseListStore()

// Whether to hide the navigation bar; component state.
const navbarShown = ref<boolean>(true)
/** Messages to display in VSnackbarQueue; component state. */
const messages = ref<SnackbarMessage[]>([])

/** Event handler for queueing message in VSnackbarQueue. */
const queueMessage = (message: SnackbarMessage) => {
  messages.value.push(message)
}

onMounted(async () => {
  await caseListStore.initialize(props.projectUuid)
})
</script>

<template>
  <v-app id="case-list">
    <v-main>
      <TheAppBar
        v-model:show-left-panel="navbarShown"
        :show-left-panel-button="true"
        :show-right-panel-button="false"
      />
      <TheNavBar :navbar-shown="navbarShown">
        <v-list-item
          prepend-icon="mdi-arrow-left"
          :href="`/project/${projectUuid}`"
        >
          <template v-if="navbarShown"> Back to Project </template>
        </v-list-item>
        <v-list-subheader v-if="navbarShown" class="text-uppercase">
          Project Overview
        </v-list-subheader>
        <v-list-item
          :class="{ 'pt-3 mt-1 border-t-thin': !navbarShown }"
          prepend-icon="mdi-format-list-bulleted-square"
          :to="{
            name: 'case-list',
            params: { project: projectUuid },
          }"
        >
          <template v-if="navbarShown"> Case List </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-chart-multiple"
          :to="{
            name: 'case-list-qc',
            params: { project: projectUuid },
          }"
        >
          <template v-if="navbarShown"> Quality Control </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-filter-settings"
          :to="{
            name: 'case-list-query-presets',
            params: { project: projectUuid },
          }"
        >
          <template v-if="navbarShown"> Query Presets </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-numeric-2-box-multiple-outline"
          :to="{
            name: 'seqvars-query-presets',
            params: { project: projectUuid },
          }"
        >
          <template v-if="navbarShown"> Query Presets (V2) </template>
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
          <QueryPresets :project-uuid="projectUuid" :preset-set="presetSet" />
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
  <VueQueryDevtools />
</template>
