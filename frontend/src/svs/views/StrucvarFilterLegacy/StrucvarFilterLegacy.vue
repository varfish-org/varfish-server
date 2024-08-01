<script setup lang="ts">
import { watch, onMounted, computed, ref } from 'vue'
import { useCaseListStore } from '@/cases/stores/caseList'
import { useProjectStore } from '@/cases/stores/project/store'
import { useSvQueryStore } from '@/svs/stores/svQuery'

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
const svQueryStore = useSvQueryStore()

const filtrationComplexityMode = computed(() => {
  switch (svQueryStore.filtrationComplexityMode) {
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
  switch (svQueryStore.filtrationComplexityMode) {
    case 'simple':
      svQueryStore.filtrationComplexityMode = 'normal'
      break
    case 'normal':
      svQueryStore.filtrationComplexityMode = 'advanced'
      break
    case 'advanced':
      svQueryStore.filtrationComplexityMode = 'dev'
      break
    case 'dev':
      svQueryStore.filtrationComplexityMode = 'simple'
      break
  }
}

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
          :prepend-icon="`mdi-numeric-${filtrationComplexityMode}-box-multiple`"
          @click="toggleFiltrationComplexityMode()"
        >
          Toggle Complexity
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
