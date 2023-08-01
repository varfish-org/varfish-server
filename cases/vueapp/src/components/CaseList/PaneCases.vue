<script setup>
import debounce from 'lodash.debounce'
import { onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import EasyDataTable from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'

import casesApi from '@cases/api/cases'
import { useCasesStore } from '@cases/stores/cases'
import { displayName, formatLargeInt, formatTimeAgo } from '@varfish/helpers'

const casesStore = useCasesStore()

const tableHeaders = [
  { text: 'Case Name', value: 'name', sortable: true },
  { text: 'Status', value: 'status', sortable: true },
  { text: 'Individuals', value: 'individuals' },
  { text: 'Small Vars', value: 'num_small_vars', sortable: true, width: 100 },
  { text: 'SVs', value: 'num_svs', sortable: true, width: 100 },
  { text: 'Creation', value: 'date_created', width: 150 },
  { text: 'Last Update', value: 'date_modified', width: 150 },
  { text: 'Shortcuts', value: 'buttons', width: 50 },
]

/** Rows to display in the table. */
const tableRows = ref([])
/** Whether the Vue3EasyDataTable is loading. */
const tableLoading = ref(false)
/** The table server options, updated by Vue3EasyDataTable. */
const tableServerOptions = ref(
  reactive({
    page: 1,
    rowsPerPage: 20,
    sortBy: null,
    sortType: 'asc',
  }),
)
/** The current search term. */
const searchTerm = ref('')

/** Load data from table as configured by tableServerOptions. */
const loadFromServer = async () => {
  const transmogrify = (row) => {
    row['indexName'] = row['index']
    delete row['index']
    return row
  }

  tableLoading.value = true
  const response = await casesApi.listCase(
    casesStore.csrfToken,
    casesStore.project.sodar_uuid,
    {
      pageNo: tableServerOptions.value.page - 1,
      pageSize: tableServerOptions.value.rowsPerPage,
      orderBy: tableServerOptions.value.sortBy,
      orderDir: tableServerOptions.value.sortType,
      queryString: searchTerm.value,
    },
  )
  tableRows.value = response.results.map((row) => transmogrify(row))
  tableLoading.value = false
}

/** Update display when pagination or sorting changed. */
watch(
  [
    () => tableServerOptions.value.page,
    () => tableServerOptions.value.rowsPerPage,
    () => tableServerOptions.value.sortBy,
    () => tableServerOptions.value.sortType,
  ],
  (
    [_newPageNo, _newRowsPerPage, _newSortBy, _newSortType],
    [_oldPageNo, _oldRowsPerPage, _oldSortBy, _oldSortType],
  ) => loadFromServer(),
)

const getIndividuals = (pedigree) => {
  return pedigree
    .map((row) => {
      return displayName(row.name)
    })
    .join(', ')
}

/** The global router object. */
const router = useRouter()

/** Navigate to the case detail. */
const navigate = (caseUuid) => {
  router.push(`/detail/${caseUuid}`)
}

/** Debounced version for reloading the table from server */
const debouncedLoadFromServer = debounce(loadFromServer, 1000, {
  leading: true,
  maxWait: 2,
  trailing: true,
})

/** Update display when search term changed. */
watch(
  () => searchTerm.value,
  (_newSearchTerm, _oldSearchTerm) => debouncedLoadFromServer(),
)

/** Load from server when mounted. */
onMounted(async () => {
  await loadFromServer()
})
</script>

<template>
  <div class="row pt-3">
    <div class="col">
      <!--      <div class="mb-3 mt-0 pl-0 pr-0">-->
      <!--        <CaseListProgressBar />-->
      <!--      </div>-->

      <div class="card mb-3 varfish-case-list-card">
        <div class="card-header d-flex">
          <h4 class="col-auto">
            <i-mdi-family-tree />
            Case List ({{ casesStore.caseCount }})
          </h4>

          <div class="col-auto ml-auto pr-0">
            <div class="input-group">
              <div class="input-group-prepend">
                <span class="input-group-text">
                  <i-mdi-account-search />
                </span>
              </div>
              <input
                type="text"
                class="form-control"
                placeholder="search text"
                v-model="searchTerm"
              />
            </div>
          </div>
        </div>

        <div class="card-body p-0 position-relative">
          <EasyDataTable
            v-model:server-options="tableServerOptions"
            table-class-name="customize-table"
            :loading="tableLoading"
            :server-items-length="casesStore.caseCount"
            :headers="tableHeaders"
            :items="tableRows"
            :rows-items="[20, 50, 200, 1000]"
            alternating
            buttons-pagination
            show-index
          >
            <template #item-name="{ sodar_uuid, name }">
              <a href="#" @click.prevent="navigate(sodar_uuid)">{{ name }}</a>
            </template>
            <template #item-individuals="{ pedigree }">
              {{ getIndividuals(pedigree) }}
            </template>
            <template #item-num_small_vars="{ num_small_vars }">
              <div class="text-right">
                {{ formatLargeInt(num_small_vars) }}
              </div>
            </template>

            <template #item-num_svs="{ num_svs }">
              <div class="text-right">
                {{ formatLargeInt(num_svs) }}
              </div>
            </template>

            <template #item-date_created="{ date_created }">
              {{ formatTimeAgo(date_created) }}
            </template>

            <template #item-date_modified="{ date_modified }">
              {{ formatTimeAgo(date_modified) }}
            </template>

            <template #item-buttons="{ sodar_uuid, num_small_vars, num_svs }">
              <div class="btn-group">
                <button
                  title="Filter small variants"
                  type="button"
                  class="btn btn-sm btn-primary"
                  style="font-size: 80%"
                  :disabled="!num_small_vars"
                  @click="
                    router.push({
                      name: 'variants-filter',
                      params: { case: sodar_uuid },
                    })
                  "
                >
                  <i-mdi-filter />
                </button>
                <button
                  title="Filter SVs"
                  type="button"
                  class="btn btn-sm btn-primary pl-2"
                  style="font-size: 80%"
                  :disabled="!num_svs"
                  @click="
                    router.push({
                      name: 'svs-filter',
                      params: { case: sodar_uuid },
                    })
                  "
                >
                  <i-mdi-filter-variant />
                </button>
              </div>
            </template>
          </EasyDataTable>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.customize-table {
  --easy-table-border: none;
  /*--easy-table-header-background-color: #2d3a4f;*/
}
</style>
