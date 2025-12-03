<script setup lang="ts">
import debounce from 'lodash.debounce'
import { Ref, computed, ref, watch } from 'vue'

import { useCaseCountQuery, useCaseListQuery } from '@/cases/queries/cases'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'
import { formatLargeInt, formatTimeAgo } from '@/varfish/helpers'

import { getIndividuals } from './lib'
import { SortBy } from './types'

/** Props used in this component. */
const props = defineProps<{
  /** The project UUID to list cases for. */
  projectUuid?: string
}>()

/** This component's events. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits<{
  message: [message: SnackbarMessage]
}>()

/** Headers to be used in the `VDataTableServer`. */
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

/** Current page in `VDataTableServer`; component state. */
const page = ref<number>(1)
/** Items per page in `VDataTableServer`; component state. */
const itemsPerPage = ref<number>(20)
/** Sort by in `VDataTableServer`; component state. */
const sortBy = ref<SortBy[]>([{ key: 'name', order: 'asc' }])
/** Search string in `VDataTableServer`; component state. */
const search = ref<string>('')
/** Table rows to display in `VDataTableServer` as obtained via TanStack Query. */
const tableRows = computed(() => caseListRes.data.value?.results ?? [])

/** Query case list data. */
const caseListRes = useCaseListQuery({
  projectUuid: computed(() => props.projectUuid),
  page: page,
  pageSize: itemsPerPage,
  orderBy: computed(() =>
    sortBy.value.length > 0 ? sortBy.value[0].key : 'name',
  ),
  orderDir: computed(() =>
    sortBy.value[0]?.order === 'desc' ? 'desc' : 'asc',
  ),
  queryString: search,
})

/** Query case count data. */
const caseCountRes = useCaseCountQuery({
  projectUuid: computed(() => props.projectUuid),
  queryString: search,
})

/** Update query settings from `VDataTableServer`, may trigger re-fetching. */
const updateQuery = async ({
  page: page$,
  itemsPerPage: itemsPerPage$,
  sortBy: sortBy$,
}: {
  page: number
  itemsPerPage: number
  sortBy: SortBy[]
}) => {
  page.value = page$
  itemsPerPage.value = itemsPerPage$
  sortBy.value = sortBy$
}

/** Debounced version of `updateQuery`. */
const updateQueryDebounced = debounce(updateQuery, 500)

// Watch for search changes and reset page to 1 to avoid loading non-existent pages
watch(search, () => {
  page.value = 1
})

// Watch for any error and emit a message on any error.
watch(
  () => caseListRes.isError,
  (value: Ref<boolean>) => {
    if (value.value) {
      emit('message', {
        text: `Failed to fetch case list: ${caseListRes.error.value?.message}`,
        color: 'error',
      })
    }
  },
)
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
    :items-length="caseCountRes.data.value?.count ?? 0"
    :loading="caseListRes.isPending.value || caseCountRes.isPending.value"
    :search="search"
    no-data-text="No matching cases found"
    item-value="name"
    @update:options="updateQueryDebounced"
  >
    <template #[`item.index`]="{ index }">
      {{ index + 1 }}
    </template>
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
      {{ getIndividuals(item.pedigree as any) }}
    </template>
    <template #[`item.num_small_vars`]="{ item }">
      <div class="text-right">
        {{ formatLargeInt(item.num_small_vars ?? 0) }}
      </div>
    </template>

    <template #[`item.num_svs`]="{ item }">
      <div class="text-right">
        {{ formatLargeInt(item.num_svs ?? 0) }}
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
