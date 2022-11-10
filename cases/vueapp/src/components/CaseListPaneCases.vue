<script setup>
import debounce from 'lodash.debounce'
import { computed, ref, watch } from 'vue'

import { AgGridVue } from 'ag-grid-vue3'

import CaseListProgressBar from './CaseListProgressBar.vue'
import { useCasesStore } from '../stores/cases.js'
import { columnDefs } from './CaseListPaneCases.values.js'
import Overlay from './Overlay.vue'

const casesStore = useCasesStore()

/** A {@code ref} around the ag-grid's {@code api}, set when the ag-grid emits {@code gridReady}. */
const gridApi = ref(null)
/** A {@code ref} around the ag-grid's {@code columnApi}, set when the ag-grid emits {@code gridReady}. */
const columnApi = ref(null)

/** The current page. */
const pageNo = ref(0)
/** The number of items per page. */
const pageSize = ref(10)
/** The current search term. */
const searchTerm = ref('')

/** Ref to the AgGridVue. */
const agGridRef = ref(null)

/**
 * Event handler for ag-grid's {@code gridReady} event.
 *
 * @param event The event as raised by the ag-grid
 */
const onGridReady = (event) => {
  gridApi.value = event.api
  columnApi.value = event.columnApi
}

/** Event handler for ag-grid's {@code firstDataRendered} event. */
const onFirstDataRendered = () => {
  gridApi.value.sizeColumnsToFit()
}

/** Default column definition for the ag-grid. */
const defaultColDef = { resizable: true, sortable: true }

/** Navigate to first page. */
const goFirstPage = () => {
  if (pageNo.value > 0) {
    pageNo.value = 0
  }
}

/** Navigate to previous page. */
const goPreviousPage = () => {
  if (pageNo.value > 0) {
    pageNo.value -= 1
  }
}

/** Navigate to next page. */
const goNextPage = () => {
  if (pageNo.value + 1 < casesStore.pageCount) {
    pageNo.value += 1
  }
}

/** Navigate to last page. */
const goLastPage = () => {
  if (pageNo.value + 1 < casesStore.pageCount) {
    pageNo.value = casesStore.pageCount - 1
  }
}

/** Debounced version for updating store's query parameters. */
const _storeUpdateQueryParams = debounce(casesStore.updateQueryParams, 1000, {
  leading: true,
  maxWait: 2,
  trailing: true,
})

watch(
  [() => pageNo.value, () => pageSize.value, () => searchTerm.value],
  (
    [newPageNo, newPageSize, newSearchTerm],
    [_oldPageNo, _oldPageSize, _oldSearchTerm]
  ) => {
    _storeUpdateQueryParams(newPageNo, newPageSize, newSearchTerm)
  }
)

/** Whether to show the overlay. */
const overlayShow = computed(() => casesStore.serverInteractions > 0)

defineExpose({
  // for test
  agGridRef,
})
</script>

<template>
  <div class="row pt-3">
    <div class="col">
      <div class="mb-3 mt-0 pl-0 pr-0">
        <CaseListProgressBar />
      </div>

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
          <AgGridVue
            ref="agGridRef"
            class="ag-theme-alpine"
            domLayout="autoHeight"
            :columnDefs="columnDefs"
            :rowData="casesStore.caseRowData"
            :defaultColDef="defaultColDef"
            :onFirstDataRendered="onFirstDataRendered"
            @grid-ready="onGridReady"
          />
          <Overlay v-if="overlayShow" />
        </div>

        <div class="card-footer d-flex pl-3 pr-3">
          <template v-if="casesStore.caseCount">
            <div>
              <select
                class="custom-select custom-select-sm"
                v-model="pageSize"
                :disabled="!casesStore.caseCount"
              >
                <option :value="10">10 items per page</option>
                <option :value="50">50 items per page</option>
                <option :value="100">100 items per page</option>
                <option :value="1000">1000 items per page</option>
              </select>
            </div>
            <div class="ml-auto">
              <i-mdi-skip-backward
                :class="{ 'text-muted': pageNo <= 0 }"
                @click="goFirstPage()"
              />
              <i-mdi-play
                style="transform: rotate(180deg)"
                :class="{ 'text-muted': pageNo <= 0 }"
                @click="goPreviousPage()"
              />
              page {{ pageNo + 1 }} of {{ casesStore.pageCount }}
              <i-mdi-play
                :class="{ 'text-muted': pageNo + 1 >= casesStore.pageCount }"
                @click="goNextPage()"
              />
              <i-mdi-skip-forward
                @click="goLastPage()"
                :class="{ 'text-muted': pageNo + 1 >= casesStore.pageCount }"
              />
            </div>
          </template>
          <div v-else class="text-muted">no data</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style src="ag-grid-community/styles/ag-grid.css"></style>
<style src="ag-grid-community/styles/ag-theme-alpine.css"></style>
<style>
.ag-theme-alpine {
  --ag-borders: none;
}
</style>
