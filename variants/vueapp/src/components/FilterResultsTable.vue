<script setup>
import { AgGridVue } from 'ag-grid-vue3'
import { computed, reactive, ref } from 'vue'
import { displayName } from '@varfish/helpers.js'
import ColumnControl from './ColumnControl.vue'
import ColumnSizeFitter from './ColumnSizeFitter.vue'
import ExportResults from './ExportResults.vue'
import { defineColumnDefs } from './FilterResultsTable.columnDefs.js'
import { declareWrapper } from '../helpers'

const goToLocus = async ({ chromosome, start, end }) => {
  const chrPrefixed = chromosome.startsWith('chr')
    ? chromosome
    : `chr${chromosome}`
  await fetch(
    `http://127.0.0.1:60151/goto?locus=${chrPrefixed}:${start}-${end}`
  )
}

/**
 * The component's props.
 */
const props = defineProps({
  /** The case with the property to display for. */
  case: Object,
  /** The results from the query to display in the table. */
  queryResults: Object,
  /** Which details to display, integer value from {@code DisplayDetails}. */
  displayDetails: Number,
  /** Which frequency information to display, integer value from {@code DisplayFrequency}. */
  displayFrequency: Number,
  /** The constraint to display, integer value from {@code DisplayConstraint}. */
  displayConstraint: Number,
  /** The additional columns to display; Integers from {@code DisplayColumns}. */
  displayColumns: Array,
  /** The extra fields information. */
  extraAnnoFields: Array,
})

/**
 * Define the emitted events.
 */
const emit = defineEmits([
  /** Variant has been selected. */
  'variantSelected',
  /** Emitted to notify about change in {@code displayDetails} prop. */
  'update:displayDetails',
  /** Emitted to notify about change in {@code displayFrequency} prop. */
  'update:displayFrequency',
  /** Emitted to notify about change in {@code displayConstraint} prop. */
  'update:displayConstraint',
  /** Emitted to notify about change in {@code displayColumns} prop. */
  'update:displayColumns',
])

/** Wrapper around {@code displayDetails} prop. */
const displayDetailsWrapper = declareWrapper(props, 'displayDetails', emit)
/** Wrapper around {@code displayFrequency} prop. */
const displayFrequencyWrapper = declareWrapper(props, 'displayFrequency', emit)
/** Wrapper around {@code displayConstraint} prop. */
const displayConstraintWrapper = declareWrapper(
  props,
  'displayConstraint',
  emit
)
/** Wrapper around {@code displayColumns} prop. */
const displayColumnsWrapper = declareWrapper(props, 'displayColumns', emit)
/** Reactive wrapper around the {@code queryResults} prop so the ag-grid can react to data being loaded. */
const rowData = reactive(props.queryResults)

/** A {@code ref} around the ag-grid's {@code api}, set when the ag-grid emits {@code gridReady}. */
const gridApi = ref(null)
/** A {@code ref} around the ag-grid's {@code columnApi}, set when the ag-grid emits {@code gridReady}. */
const columnApi = ref(null)

/**
 * Configuration for the ag-grid row to color them based on flags.
 */
const rowClassRules = {
  'row-positive': "data.flag_summary === 'positive'",
  'row-uncertain': "data.flag_summary === 'uncertain'",
  'row-negative': "data.flag_summary === 'negative'",
  'row-wip': (params) => {
    return (
      params.data.flag_summary === 'empty' &&
      (params.data.flag_visual !== 'empty' ||
        params.data.flag_validation !== 'empty' ||
        params.data.flag_molecular !== 'empty' ||
        params.data.flag_phenotype_match !== 'empty' ||
        params.data.flag_candidate === true ||
        params.data.flag_doesnt_segregate === true ||
        params.data.flag_final_causative === true ||
        params.data.flag_for_validation === true ||
        params.data.flag_no_disease_association === true ||
        params.data.flag_segregates === true)
    )
  },
}

/** Default column definition for the ag-grid. */
const defaultColDef = { resizable: true }

/** Computed property that defines the column definitions for the genotype columns. */
const genotypesWrapper = computed(() => {
  if (!props.case || !props.case.pedigree) {
    return []
  } else {
    return props.case.pedigree.map((member) => {
      return {
        field: 'genotype_' + displayName(member.name),
        headerName: displayName(member.name),
        valueGetter: (params) => {
          return params.data.genotype[member.name].gt
        },
        sortable: true,
        filter: 'agTextColumnFilter',
        filterParams: {
          filterOptions: ['equals', 'notEqual'],
        },
      }
    })
  }
})

/**
 * Define the column definitions for the ag-grid as a reactive value.
 *
 * We have moved the long array literal for defining this into its own file to keep this component file easier to read.
 */
const columnDefs = reactive(
  defineColumnDefs({
    displayFrequency: displayFrequencyWrapper.value,
    displayConstraint: displayConstraintWrapper.value,
    displayDetails: displayDetailsWrapper.value,
    displayColumns: displayColumnsWrapper.value,
    genotypes: genotypesWrapper.value,
    extraAnnoFields: props.extraAnnoFields,
  })
)

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

/** Event handler for ag-grid's {@code cellClicked} event. */
const onCellClicked = (event) => {
  if (!['selector', 'variant_icons', 'igv'].includes(event.column.getColId())) {
    emit('variantSelected', {
      gridRow: event.node,
      gridApi: event.api,
      smallVariant: event.data,
    })
  }
}
</script>

<template>
  <div class="card mb-0 h-100">
    <div class="card-header d-flex flex-row pt-1 pb-1">
      <div class="pr-3 align-self-start record-count">
        <div>
          <label class="font-weight-bold small mb-0 text-nowrap">
            # Records
          </label>
        </div>
        <div class="text-center">
          <span class="btn btn-sm btn-outline-secondary" id="results-button">
            {{ rowData.length }}
          </span>
        </div>
      </div>
      <ColumnSizeFitter :column-api="columnApi" :grid-api="gridApi" />
      <ColumnControl
        :column-api="columnApi"
        :extra-anno-fields="props.extraAnnoFields"
        v-model:display-details="displayDetailsWrapper"
        v-model:display-frequency="displayFrequencyWrapper"
        v-model:display-constraint="displayConstraintWrapper"
        v-model:display-columns="displayColumnsWrapper"
      />
      <ExportResults />
    </div>
    <div class="card-body p-0 b-0">
      <!-- ag-grid itself -->
      <AgGridVue
        style="height: 100%"
        class="ag-theme-alpine"
        :columnDefs="columnDefs"
        :rowData="rowData"
        :defaultColDef="defaultColDef"
        :onFirstDataRendered="onFirstDataRendered"
        :onCellClicked="onCellClicked"
        :rowClassRules="rowClassRules"
        @grid-ready="onGridReady"
      />
    </div>
  </div>
</template>

<style>
/* pathogenic */
.row-positive {
  background-color: #dc354533 !important;
}
/* uncertain */
.row-uncertain {
  background-color: #ffc10733 !important;
}
/* benign */
.row-negative {
  background-color: #28a74533 !important;
}
/* wip */
.row-wip {
  background-color: #6c757d33 !important;
}
</style>

<style src="ag-grid-community/styles/ag-grid.css"></style>
<style src="ag-grid-community/styles/ag-theme-alpine.css"></style>
<style>
.record-count .btn {
  height: calc(1.5em + 0.5rem + 2px);
}
.sodar-app-content {
  padding-bottom: 0px;
}
.ag-theme-alpine {
  --ag-borders: none;
}
</style>
