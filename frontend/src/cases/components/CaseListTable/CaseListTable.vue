<script setup lang="ts">
import { client } from '@hey-api/client-fetch'
import { CasesService } from '@varfish-org/varfish-api/lib'
import debounce from 'lodash.debounce'
import { onMounted, ref } from 'vue'

import { useCaseListStore } from '@/cases/stores/caseList'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'
import { formatLargeInt, formatTimeAgo } from '@/varfish/helpers'

import { getIndividuals } from './lib'
import { Case, SortBy } from './types'

/** Props used in this component. */
const props = defineProps<{
  projectUuid?: string
}>()

/** This component's events. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits<{
  message: [message: SnackbarMessage]
}>()

const caseListStore = useCaseListStore()

const headers = [
  { title: '#', key: 'index', width: 50, sortable: false },
  { title: 'Case Name', key: 'name', width: 100, sortable: true },
  { title: 'Status', key: 'status', width: 100, sortable: true },
  { title: 'Individuals', key: 'individuals' },
  { title: 'Case Version', key: 'case_version', sortable: true, width: 100 },
  { title: 'Small Vars', key: 'num_small_vars', sortable: true, width: 100 },
  { title: 'SVs', key: 'num_svs', sortable: true, width: 100 },
  { title: 'Creation', key: 'date_created', width: 150 },
  { title: 'Last Update', key: 'date_modified', width: 150 },
  { title: 'Shortcuts', key: 'buttons', width: 50 },
]

const page = ref<number>(1)
const itemsPerPage = ref<number>(20)
const sortBy = ref<SortBy[]>([{ key: 'name', order: 'asc' }])
const loading = ref<boolean>(false)
const search = ref<string>('')

const tableRows = ref<Case[]>([])

/** Load data from table as configured by tableServerOptions. */
const loadItems = async ({
  page,
  itemsPerPage,
  sortBy,
}: {
  page: number
  itemsPerPage: number
  sortBy: SortBy[]
}) => {
  if (props.projectUuid === undefined) {
    return // bail out
  }

  // Wait for initialization of caseListStore to finish.
  await caseListStore.initialize(props.projectUuid)

  const transmogrify = (row: any, index: number) => {
    row['index'] = (page - 1) * itemsPerPage + index + 1
    return row
  }

  const orderBy = sortBy.length > 0 ? sortBy[0].key : 'name'
  const orderDir =
    sortBy.length > 0 ? (sortBy[0].order === 'desc' ? 'desc' : 'asc') : 'asc'

  loading.value = true
  const response = await CasesService.casesApiCaseListList({
    client,
    path: { project: props.projectUuid },
    query: {
      page,
      pageSize: itemsPerPage,
      order_by: orderBy,
      order_dir: orderDir,
      q: search.value,
    },
  })
  // Bail out and notify parent if there was an error.
  if (!response.data) {
    emit('message', {
      text: 'Failed to load cases',
      color: 'error',
    })
    return
  }

  tableRows.value = (response.data.results ?? []).map(transmogrify)
  loading.value = false
}

const loadItemDebounced = debounce(loadItems, 500)

onMounted(() => {
  loadItemDebounced({
    page: page.value,
    itemsPerPage: itemsPerPage.value,
    sortBy: sortBy.value,
  })
})
</script>

<template>
  <h2>Cases</h2>

  <v-sheet class="pa-3 rounded-0">
    <v-row no-gutter>
      <v-col cols="6"> </v-col>
      <v-col cols="6">
        <v-text-field
          v-model="search"
          density="compact"
          label="Filter cases"
          append-inner-icon="mdi-magnify"
          variant="outlined"
          hide-details
        ></v-text-field>
      </v-col>
    </v-row>
  </v-sheet>
  <v-data-table-server
    v-model:page="page"
    v-model:items-per-page="itemsPerPage"
    v-model:sort-by="sortBy"
    :headers="headers"
    :items="tableRows"
    :items-length="caseListStore.caseCount ?? 0"
    :loading="loading"
    :search="search"
    no-data-text="No matching cases found"
    item-value="name"
    @update:options="loadItemDebounced"
  >
    <template #[`item.name`]="{ item }">
      <router-link
        :to="{
          name: 'case-detail-overview',
          params: { project: props.projectUuid, case: item.sodar_uuid },
        }"
      >
        {{ item.name }}
      </router-link>
    </template>
    <template #[`item.individuals`]="{ item }">
      {{ getIndividuals(item.pedigree) }}
    </template>
    <template #[`item.num_small_vars`]="{ item }">
      <div class="text-right">
        {{ formatLargeInt(item.num_small_vars) }}
      </div>
    </template>

    <template #[`item.num_svs`]="{ item }">
      <div class="text-right">
        {{ formatLargeInt(item.num_svs) }}
      </div>
    </template>

    <template #[`item.date_created`]="{ item }">
      {{ formatTimeAgo(item.date_created) }}
    </template>

    <template #[`item.date_modified`]="{ item }">
      {{ formatTimeAgo(item.date_modified) }}
    </template>
    <template #[`item.buttons`]="{ item }">
      <router-link
        :to="{
          name: 'variants-filter',
          params: { project: props.projectUuid, case: item.sodar_uuid },
        }"
      >
        <v-icon size="small" icon="mdi-filter" class="me-2"></v-icon>
      </router-link>
      <router-link
        :to="{
          name: 'svs-filter',
          params: { project: props.projectUuid, case: item.sodar_uuid },
        }"
      >
        <v-icon size="small" icon="mdi-filter-variant"></v-icon>
      </router-link>
    </template>
  </v-data-table-server>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
