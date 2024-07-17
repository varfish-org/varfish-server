<script setup lang="ts">
import { watch, onMounted, ref } from 'vue'
import { useCaseListStore } from '@/cases/stores/caseList'
import { useProjectStore } from '@/cases/stores/project/store'

import SvFilterApp from '@/svs/components/SvFilterApp.vue'
import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import TheNavBar from '@/cases/components/TheNavBar/TheNavBar.vue'

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
</script>

<template>
  <v-app id="strucvar-filter-legacy">
    <v-main>
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
          SV Analysis
        </v-list-subheader>
        <v-list-item
          prepend-icon="mdi-filter"
          :to="{
            name: 'variants-filter',
            params: { case: caseUuid },
          }"
        >
          Go To Variant Filtration
        </v-list-item>
        <v-list-subheader class="text-uppercase">
          Analysis Info
        </v-list-subheader>
        <v-list-item
          prepend-icon="mdi-button-cursor"
          @click="filterFormVisible = !filterFormVisible"
        >
          Toggle Form
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-card-text-outline"
          @click="logsVisible = !logsVisible"
        >
          Toggle Logs
        </v-list-item>
      </TheNavBar>
      <SvFilterApp
        :project-uuid="props.projectUuid"
        :case-uuid="props.caseUuid"
        v-model:filter-form-visible="filterFormVisible"
        v-model:query-logs-visible="logsVisible"
      />
    </v-main>
  </v-app>
</template>
