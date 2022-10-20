<script setup>
import { AgGridVue } from 'ag-grid-vue3'

import CaseListProgressBar from './CaseListProgressBar.vue'
import { useCasesStore } from '../stores/cases.js'
import { ref } from 'vue'
import { columnDefs } from './CaseListPaneCases.values.js'

const casesStore = useCasesStore()

/** A {@code ref} around the ag-grid's {@code api}, set when the ag-grid emits {@code gridReady}. */
const gridApi = ref(null)
/** A {@code ref} around the ag-grid's {@code columnApi}, set when the ag-grid emits {@code gridReady}. */
const columnApi = ref(null)

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

defineExpose({
  // for test
  agGridRef,
})
</script>

<template>
  <div class="row pt-3 flex-grow-1 d-flex flex-column">
    <div class="col flex-grow-1 d-flex flex-column">
      <div class="mb-3 mt-0 pl-0 pr-0">
        <CaseListProgressBar />
      </div>

      <!--      <div>{{ columnDefs }}</div>-->
      <!--      <div>{{ casesStore.caseRowData}}</div>-->

      <div class="card mb-3 varfish-case-list-card d-flex flex-grow-1">
        <h4 class="card-header">
          <i-mdi-family-tree />
          Case List
        </h4>
        <div class="card-body p-0 flex-grow-1">
          <AgGridVue
            ref="agGridRef"
            style="height: 300px"
            class="ag-theme-alpine"
            :columnDefs="columnDefs"
            :rowData="casesStore.caseRowData"
            :defaultColDef="defaultColDef"
            :onFirstDataRendered="onFirstDataRendered"
            @grid-ready="onGridReady"
          />
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
