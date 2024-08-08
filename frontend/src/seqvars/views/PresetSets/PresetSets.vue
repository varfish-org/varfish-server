<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import TheNavBar from '@/cases/components/TheNavBar/TheNavBar.vue'
import PresetsEditor from '@/seqvars/components/PresetsEditor/PresetsEditor.vue'

import { useProjectStore } from '@/cases/stores/project/store'
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { type SnackbarMessage } from './lib'

const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** UUID of the current preset set. */
  presetSet?: string
  /** UUID of the current preset set version. */
  presetSetVersion?: string
}>()

const projectStore = useProjectStore()
const seqvarsPresetsStore = useSeqvarsPresetsStore()

/** Whether to hide the navigation bar; component state. */
const navbarShown = ref<boolean>(true)
/** Messages to display in VSnackbarQueue; component state. */
const messages = ref<SnackbarMessage[]>([])

/** (Re-)initialize the stores. */
const initializeStores = async () => {
  await Promise.all([
    projectStore.initialize(props.projectUuid),
    seqvarsPresetsStore.initialize(props.projectUuid),
  ])
}

/** Event handler for queueing message in VSnackbarQueue. */
const queueMessage = (message: SnackbarMessage) => {
  messages.value.push(message)
}

// Initialize case list store on mount.
onMounted(async () => {
  await initializeStores()
})
// Re-initialize case list store when the project changes.
watch(
  () => props.projectUuid,
  async () => {
    await initializeStores()
  },
)
</script>

<template>
  <v-app id="seqvars-presets-sets">
    <v-main>
      <TheAppBar
        :show-left-panel-button="true"
        :show-right-panel-button="false"
        v-model:show-left-panel="navbarShown"
      />
      <TheNavBar :navbar-shown="navbarShown">
        <v-list-item
          prepend-icon="mdi-arrow-left"
          :href="`/project/${projectStore.projectUuid}`"
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
            params: { project: projectStore.projectUuid },
          }"
        >
          <template v-if="navbarShown"> Case List </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-chart-multiple"
          :to="{
            name: 'case-list-qc',
            params: { project: projectStore.projectUuid },
          }"
        >
          <template v-if="navbarShown"> Quality Control </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-filter-settings"
          :to="{
            name: 'case-list-query-presets',
            params: { project: projectStore.projectUuid },
          }"
        >
          <template v-if="navbarShown"> Query Presets </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-numeric-2-box-multiple-outline"
          :to="{
            name: 'seqvars-query-presets',
            params: { project: projectStore.projectUuid },
          }"
        >
          <template v-if="navbarShown"> Query Presets (V2) </template>
        </v-list-item>
      </TheNavBar>
      <v-container class="py-2 px-6" fluid>
        <PresetsEditor
          :project-uuid="projectUuid"
          :preset-set="presetSet"
          :preset-set-version="presetSetVersion"
          @message="queueMessage"
        />
      </v-container>
    </v-main>
    <v-snackbar-queue
      v-model="messages"
      timer="5000"
      close-on-content-click
    ></v-snackbar-queue>
  </v-app>
</template>
