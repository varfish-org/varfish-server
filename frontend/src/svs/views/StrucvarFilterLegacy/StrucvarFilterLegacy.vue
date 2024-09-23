<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import TheNavBar from '@/cases/components/TheNavBar/TheNavBar.vue'
import { useCaseListStore } from '@/cases/stores/caseList'
import { useProjectStore } from '@/cases/stores/project/store'
import SvFilterApp from '@/svs/components/SvFilterApp.vue'
import { useSvQueryStore } from '@/svs/stores/svQuery'

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
const navbarShown = ref<boolean>(true)

const filterFormVisible = ref<boolean>(true)
const logsVisible = ref<boolean>(false)
</script>

<template>
  <v-app id="strucvar-filter-legacy">
    <v-main>
      <TheAppBar
        :show-left-panel-button="true"
        :show-right-panel-button="false"
        v-model:show-left-panel="navbarShown"
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
        <v-list-subheader class="text-uppercase" v-if="navbarShown">
          SV Analysis
        </v-list-subheader>
        <v-list-item
          :class="{ 'pt-3 mt-1 border-t-thin': !navbarShown }"
          prepend-icon="mdi-filter"
          :to="{
            name: 'variants-filter',
            params: { case: caseUuid },
          }"
        >
          <template v-if="navbarShown"> Go To Variant Filtration </template>
        </v-list-item>
        <v-list-subheader class="text-uppercase" v-if="navbarShown">
          Analysis Info
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
