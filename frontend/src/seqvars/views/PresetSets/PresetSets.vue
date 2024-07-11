<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import TheNavBar from '@/cases/components/TheNavBar/TheNavBar.vue'
import PresetsEditor from '@/seqvars/components/PresetsEditor/PresetsEditor.vue'

import { useProjectStore } from '@/cases/stores/project/store'
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'

const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** Identifier of the current preset set. */
  presetSet?: string
}>()

const projectStore = useProjectStore()
const seqvarsPresetsStore = useSeqvarsPresetsStore()

// Whether to hide the navigation bar; component state.
const navbarHidden = ref<boolean>(false)

/** (Re-)initialize the stores. */
const initializeStores = async () => {
  await Promise.all([
    projectStore.initialize(props.projectUuid),
    seqvarsPresetsStore.initialize(props.projectUuid),
  ])
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
    <TheAppBar v-model:navbar-hidden="navbarHidden" />
    <TheNavBar :navbar-hidden="navbarHidden">
      <v-list-item
        prepend-icon="mdi-arrow-left"
        :href="`/project/${projectStore.projectUuid}`"
      >
        Back to Project
      </v-list-item>
      <v-list-subheader class="text-uppercase">
        Project Overview
      </v-list-subheader>
      <v-list-item
        prepend-icon="mdi-format-list-bulleted-square"
        :to="{
          name: 'case-list',
          params: { project: projectStore.projectUuid },
        }"
      >
        Case List
      </v-list-item>
      <v-list-item
        prepend-icon="mdi-chart-multiple"
        :to="{
          name: 'case-list-qc',
          params: { project: projectStore.projectUuid },
        }"
      >
        Quality Control
      </v-list-item>
      <v-list-item
        prepend-icon="mdi-filter-settings"
        :to="{
          name: 'case-list-query-presets',
          params: { project: projectStore.projectUuid },
        }"
      >
        Query Presets
      </v-list-item>
      <v-list-item
        prepend-icon="mdi-numeric-2-box-multiple-outline"
        :to="{
          name: 'seqvars-query-presets',
          params: { project: projectStore.projectUuid },
        }"
      >
        Query Presets (NEW)
      </v-list-item>
    </TheNavBar>
    <v-main>
      <v-container class="py-2 px-6" fluid>
        <PresetsEditor :project-uuid="projectUuid" :preset-set="presetSet" />
      </v-container>
    </v-main>
  </v-app>
</template>
