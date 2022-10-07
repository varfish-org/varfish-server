<template>
  <label for="columnSizeFitter" class="small">Column Size</label>
  <div class="btn-group pl-2" id="columnSizeFitter">
    <button @click="sizeToFit" class="btn btn-outline-secondary">Fit</button>
    <button @click="autoSizeAll" class="btn btn-outline-secondary">Auto</button>
  </div>
  <select
    v-model="queryStore.displayDetails"
    class="custom-select pl-2"
    @change="selectDetailColumn"
    style="width: 150px"
  >
    <option
      v-for="option in DisplayDetails"
      :value="option.value"
      :key="option"
    >
      {{ option.text }}
    </option>
  </select>
  <select
    class="custom-select"
    style="width: 150px"
    @change="selectFrequencyColumn"
    v-model="queryStore.displayFrequency"
  >
    <option
      v-for="option in DisplayFrequencies"
      :value="option.value"
      :key="option"
    >
      {{ option.text }}
    </option>
  </select>
  <select
    @change="selectConstraintColumn"
    v-model="queryStore.displayConstraint"
    class="custom-select"
    style="width: 150px"
  >
    <option
      v-for="option in DisplayConstraints"
      :value="option.value"
      :key="option"
    >
      {{ option.text }}
    </option>
  </select>
  <select
    @change="selectDisplayColumns"
    v-model="queryStore.displayColumns"
    id="result-columns-selector"
    class="selectpicker"
    multiple
  >
    <option
      v-for="option in DisplayColumns"
      :value="option.value"
      :key="option"
    >
      {{ option.text }}
    </option>
  </select>
  <AgGridVue
    style="height: 800px"
    class="ag-theme-alpine"
    :columnDefs="columnDefs"
    :rowData="rowData"
    :defaultColDef="defaultColDef"
    :onFirstDataRendered="onFirstDataRendered"
    :onCellClicked="onCellClicked"
    :rowClassRules="rowClassRules"
    @grid-ready="onGridReady"
  >
  </AgGridVue>
  <!-- Variant Details Modal -->
  <div
    class="modal fade"
    id="variantDetailsModal"
    tabindex="-1"
    aria-labelledby="variantDetailsModalLabel"
    aria-hidden="true"
    style="z-index: 10000"
  >
    <div
      class="modal-dialog modal-dialog-scrollable modal-xl"
      role="document"
      style="max-width: 100%; margin: 10px"
    >
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title" id="variantDetailsModalLabel">
            Variant Details for
            <template v-if="detailsStore.smallVariant">
              {{ detailsStore.smallVariant.chromosome }}:{{
                detailsStore.smallVariant.start.toLocaleString()
              }}{{ detailsStore.smallVariant.reference }}>{{
                detailsStore.smallVariant.alternative
              }}
            </template>
            <span v-else>
              ...
              <i
                class="iconify spin small"
                data-icon="fa-solid:circle-notch"
              ></i>
            </span>
          </h3>
          <button
            type="button"
            class="close"
            data-dismiss="modal"
            aria-label="Close"
          >
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <span v-if="detailsStore.fetched">
            <SmallVariantDetails />
          </span>
          <div v-else class="alert alert-info">
            <i class="iconify spin" data-icon="fa-solid:circle-notch"></i
            >&nbsp;<strong>Loading details ...</strong>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import { AgGridVue } from 'ag-grid-vue3'
import { filterQueryStore } from '@variants/stores/filterQuery'
import { variantDetailsStore } from '@variants/stores/variantDetails'
import { reactive, ref } from 'vue'
import { storeToRefs } from 'pinia'
import {
  DisplayDetails,
  DisplayFrequencies,
  DisplayConstraints,
  DisplayColumns,
} from '@variants/enums'
import { displayName } from '@variants/helpers'
import SmallVariantFilterResultsTableVariantIcons from './SmallVariantFilterResultsTableVariantIcons.vue'
import SmallVariantFilterResultsTableGeneIcons from './SmallVariantFilterResultsTableGeneIcons.vue'
import SmallVariantFilterResultsTableClinvar from './SmallVariantFilterResultsTableClinvar.vue'
import SmallVariantDetails from './SmallVariantDetails.vue'

export default {
  components: {
    AgGridVue,
    SmallVariantFilterResultsTableVariantIcons,
    SmallVariantFilterResultsTableGeneIcons,
    SmallVariantFilterResultsTableClinvar,
    SmallVariantDetails,
  },
  setup() {
    // Get some variables from the store
    const queryStore = filterQueryStore()
    const detailsStore = variantDetailsStore()
    const {
      queryResults,
      displayFrequency,
      displayConstraint,
      displayDetails,
      displayColumns,
      previousQueryDetails,
    } = storeToRefs(queryStore)
    // Define ag-grid-related variables
    const rowData = reactive(queryResults)
    const gridApi = ref(null)
    const columnApi = ref(null)
    const onGridReady = (params) => {
      gridApi.value = params.api
      columnApi.value = params.columnApi
    }
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
    const defaultColDef = { resizable: true }
    // Define header lines for genotypes
    let genotypes = []
    for (const member of queryStore.case.pedigree) {
      genotypes.push({
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
      })
    }
    function getSymbol(params) {
      return params.data.symbol ? params.data.symbol : params.data.gene_symbol
    }
    const columnDefs = reactive([
      {
        field: 'selector',
        headerName: '',
        cellRenderer: () => {
          return '<input type="checkbox">'
        },
        resizable: false,
        width: 50,
        suppressSizeToFit: true,
      },
      {
        field: 'index',
        headerName: '',
        valueGetter: 'node.rowIndex + 1',
        type: 'rightAligned',
        cellRenderer: (params) => {
          return '<span class="text-muted">#' + params.value + '</span>'
        },
        resizable: false,
        width: 70,
        suppressSizeToFit: true,
      },
      {
        field: 'variant_icons',
        headerName: 'variant icons',
        cellRenderer: 'SmallVariantFilterResultsTableVariantIcons',
        resizable: false,
        width: 145,
        suppressSizeToFit: true,
      },
      {
        field: 'position',
        headerName: 'position',
        valueGetter: (params) => {
          return (
            (params.data.chromosome.startsWith('chr') ? '' : 'chr') +
            params.data.chromosome +
            ':' +
            params.data.start.toLocaleString()
          )
        },
        hide: displayDetails.value !== DisplayDetails.Coordinates.value,
      },
      {
        field: 'reference',
        headerName: 'ref',
        hide: displayDetails.value !== DisplayDetails.Coordinates.value,
      },
      {
        field: 'alternative',
        headerName: 'alt',
        hide: displayDetails.value !== DisplayDetails.Coordinates.value,
      },
      {
        field: 'clinvar',
        headerName: 'clinvar summary',
        hide: displayDetails.value !== DisplayDetails.Clinvar.value,
        cellRenderer: 'SmallVariantFilterResultsTableClinvar',
      },
      {
        field: 'exac_frequency',
        headerName: 'frequency',
        hide: displayFrequency.value !== DisplayFrequencies.Exac.value,
        valueFormatter: (params) => {
          return parseFloat(params.value).toFixed(5)
        },
        sortable: true,
      },
      {
        field: 'exac_homozygous',
        headerName: '#hom',
        hide: displayFrequency.value !== DisplayFrequencies.Exac.value,
        sortable: true,
      },
      {
        field: 'thousand_genomes_frequency',
        headerName: 'frequency',
        hide:
          displayFrequency.value !== DisplayFrequencies.ThousandGenomes.value,
        valueFormatter: (params) => {
          return parseFloat(params.value).toFixed(5)
        },
        sortable: true,
      },
      {
        field: 'thousand_genomes_homozygous',
        headerName: '#hom',
        hide:
          displayFrequency.value !== DisplayFrequencies.ThousandGenomes.value,
        sortable: true,
      },
      {
        field: 'gnomad_exomes_frequency',
        headerName: 'frequency',
        hide: displayFrequency.value !== DisplayFrequencies.GnomadExomes.value,
        valueFormatter: (params) => {
          return parseFloat(params.value).toFixed(5)
        },
        sortable: true,
      },
      {
        field: 'gnomad_exomes_homozygous',
        headerName: '#hom',
        hide: displayFrequency.value !== DisplayFrequencies.GnomadExomes.value,
        sortable: true,
      },
      {
        field: 'gnomad_genomes_frequency',
        headerName: 'frequency',
        hide: displayFrequency.value !== DisplayFrequencies.GnomadGenomes.value,
        valueFormatter: (params) => {
          return parseFloat(params.value).toFixed(5)
        },
        sortable: true,
      },
      {
        field: 'gnomad_genomes_homozygous',
        headerName: '#hom',
        hide: displayFrequency.value !== DisplayFrequencies.GnomadGenomes.value,
        sortable: true,
      },
      {
        field: 'inhouse_carriers',
        headerName: '#carriers',
        hide: displayFrequency.value !== DisplayFrequencies.InhouseDb.value,
        sortable: true,
      },
      {
        field: 'inhouse_hom_alt',
        headerName: '#hom',
        hide: displayFrequency.value !== DisplayFrequencies.InhouseDb.value,
        sortable: true,
      },
      {
        field: 'mtdb_frequency',
        headerName: 'frequency',
        hide: displayFrequency.value !== DisplayFrequencies.MtDb.value,
        valueFormatter: (params) => {
          return parseFloat(params.value).toFixed(5)
        },
        sortable: true,
      },
      {
        field: 'mtdb_count',
        headerName: '#hom',
        hide: displayFrequency.value !== DisplayFrequencies.MtDb.value,
        sortable: true,
      },
      {
        field: 'helixmtdb_frequency',
        headerName: 'frequency',
        hide: displayFrequency.value !== DisplayFrequencies.HelixMtDb.value,
        valueFormatter: (params) => {
          return parseFloat(params.value).toFixed(5)
        },
        sortable: true,
      },
      {
        field: 'helixmtdb_hom_count',
        headerName: '#hom',
        hide: displayFrequency.value !== DisplayFrequencies.HelixMtDb.value,
        sortable: true,
      },
      {
        field: 'mitomap_frequency',
        headerName: 'frequency',
        hide: displayFrequency.value !== DisplayFrequencies.Mitomap.value,
        valueFormatter: (params) => {
          return parseFloat(params.value).toFixed(5)
        },
        sortable: true,
      },
      {
        field: 'mitomap_count',
        headerName: '#hom',
        hide: displayFrequency.value !== DisplayFrequencies.Mitomap.value,
        sortable: true,
      },
      {
        field: 'exac_pLI',
        headerName: 'pLI',
        hide: displayConstraint.value !== DisplayConstraints.ExacPli.value,
        valueFormatter: (params) => {
          return parseFloat(params.value).toFixed(3)
        },
        sortable: true,
      },
      {
        field: 'exac_mis_z',
        headerName: 'Z mis',
        hide: displayConstraint.value !== DisplayConstraints.ExacZMis.value,
        valueFormatter: (params) => {
          return parseFloat(params.value).toFixed(3)
        },
        sortable: true,
      },
      {
        field: 'exac_syn_z',
        headerName: 'Z syn',
        hide: displayConstraint.value !== DisplayConstraints.ExacZSyn.value,
        valueFormatter: (params) => {
          return parseFloat(params.value).toFixed(3)
        },
        sortable: true,
      },
      {
        field: 'gnomad_loeuf',
        headerName: 'LOEUF',
        hide: displayConstraint.value !== DisplayConstraints.GnomadLoeuf.value,
        valueFormatter: (params) => {
          return parseFloat(params.value).toFixed(3)
        },
        sortable: true,
      },
      {
        field: 'gnomad_pLI',
        headerName: 'pLI',
        hide: displayConstraint.value !== DisplayConstraints.GnomadPli.value,
        valueFormatter: (params) => {
          return parseFloat(params.value).toFixed(3)
        },
        sortable: true,
      },
      {
        field: 'gnomad_mis_z',
        headerName: 'Z mis',
        hide: displayConstraint.value !== DisplayConstraints.GnomadZMis.value,
        sortable: true,
      },
      {
        field: 'gnomad_syn_z',
        headerName: 'Z syn',
        hide: displayConstraint.value !== DisplayConstraints.GnomadZSyn.value,
        sortable: true,
      },
      {
        field: 'gene',
        headerName: 'gene',
        valueGetter: getSymbol,
        sortable: true,
        filter: 'agTextColumnFilter',
        filterParams: {
          filterOptions: ['contains'],
          caseSensitive: false,
        },
      },
      {
        field: 'gene_icons',
        headerName: 'gene icons',
        cellRenderer: 'SmallVariantFilterResultsTableGeneIcons',
      },
      {
        headerName: 'effect',
        field: 'effect_summary',
        valueGetter: (params) => {
          return [null, 'p.?', 'p.='].includes(params.data.hgvs_p)
            ? params.data.hgvs_c
            : params.data.hgvs_p
        },
        hide: !displayColumns.value.includes(DisplayColumns.Effect.value),
      },
      {
        field: 'effect',
        valueFormatter: (params) => {
          return params.value.join(', ')
        },
        headerName: 'effect text',
        hide: !displayColumns.value.includes(DisplayColumns.EffectText.value),
      },
      {
        field: 'hgvs_p',
        headerName: 'hgvs_p',
        hide: !displayColumns.value.includes(
          DisplayColumns.EffectProtein.value
        ),
      },
      {
        field: 'hgvs_c',
        headerName: 'hgvs_c',
        hide: !displayColumns.value.includes(DisplayColumns.EffectCdna.value),
      },
      {
        field: 'exon_dist',
        headerName: 'exon dist',
        hide: !displayColumns.value.includes(
          DisplayColumns.DistanceSplicesite.value
        ),
      },
      ...genotypes,
      {
        field: 'igv',
        headerName: '',
        cellRenderer: (params) => {
          return '<a class="btn btn-sm badge-secondary" style="font-size: 80%" :href="`http://127.0.0.1:60151/goto?locus=chr${params.data.chromosome}:${params.data.start}-${params.data.end}`">IGV</a>'
        },
      },
    ])
    // Define functions for interactive column activation/selection
    const selectDetailColumn = () => {
      columnApi.value.setColumnsVisible(
        ['position', 'reference', 'alternative'],
        displayDetails.value === DisplayDetails.Coordinates.value
      )
      columnApi.value.setColumnVisible(
        'clinvar',
        displayDetails.value === DisplayDetails.Clinvar.value
      )
    }
    const selectFrequencyColumn = () => {
      columnApi.value.setColumnsVisible(
        ['exac_frequency', 'exac_homozygous'],
        displayFrequency.value === DisplayFrequencies.Exac.value
      )
      columnApi.value.setColumnsVisible(
        ['thousand_genomes_frequency', 'thousand_genomes_homozygous'],
        displayFrequency.value === DisplayFrequencies.ThousandGenomes.value
      )
      columnApi.value.setColumnsVisible(
        ['gnomad_exomes_frequency', 'gnomad_exomes_homozygous'],
        displayFrequency.value === DisplayFrequencies.GnomadExomes.value
      )
      columnApi.value.setColumnsVisible(
        ['gnomad_genomes_frequency', 'gnomad_genomes_homozygous'],
        displayFrequency.value === DisplayFrequencies.GnomadGenomes.value
      )
      columnApi.value.setColumnsVisible(
        ['inhouse_carriers', 'inhouse_hom_alt'],
        displayFrequency.value === DisplayFrequencies.InhouseDb.value
      )
      columnApi.value.setColumnsVisible(
        ['mtdb_frequency', 'mtdb_count'],
        displayFrequency.value === DisplayFrequencies.MtDb.value
      )
      columnApi.value.setColumnsVisible(
        ['helixmtdb_frequency', 'helixmtdb_hom_count'],
        displayFrequency.value === DisplayFrequencies.HelixMtDb.value
      )
      columnApi.value.setColumnsVisible(
        ['mitomap_frequency', 'mitomap_count'],
        displayFrequency.value === DisplayFrequencies.Mitomap.value
      )
    }
    const selectConstraintColumn = () => {
      columnApi.value.setColumnVisible(
        'exac_pLI',
        displayConstraint.value === DisplayConstraints.ExacPli.value
      )
      columnApi.value.setColumnVisible(
        'exac_mis_z',
        displayConstraint.value === DisplayConstraints.ExacZMis.value
      )
      columnApi.value.setColumnVisible(
        'exac_syn_z',
        displayConstraint.value === DisplayConstraints.ExacZSyn.value
      )
      columnApi.value.setColumnVisible(
        'gnomad_loeuf',
        displayConstraint.value === DisplayConstraints.GnomadLoeuf.value
      )
      columnApi.value.setColumnVisible(
        'gnomad_pLI',
        displayConstraint.value === DisplayConstraints.GnomadPli.value
      )
      columnApi.value.setColumnVisible(
        'gnomad_mis_z',
        displayConstraint.value === DisplayConstraints.GnomadZMis.value
      )
      columnApi.value.setColumnVisible(
        'gnomad_syn_z',
        displayConstraint.value === DisplayConstraints.GnomadZSyn.value
      )
    }
    const selectDisplayColumns = () => {
      columnApi.value.setColumnVisible(
        'effect_summary',
        displayColumns.value.includes(DisplayColumns.Effect.value)
      )
      columnApi.value.setColumnVisible(
        'effect',
        displayColumns.value.includes(DisplayColumns.EffectText.value)
      )
      columnApi.value.setColumnVisible(
        'hgvs_p',
        displayColumns.value.includes(DisplayColumns.EffectProtein.value)
      )
      columnApi.value.setColumnVisible(
        'hgvs_c',
        displayColumns.value.includes(DisplayColumns.EffectCdna.value)
      )
      columnApi.value.setColumnVisible(
        'exon_dist',
        displayColumns.value.includes(DisplayColumns.DistanceSplicesite.value)
      )
    }

    // Return variables and functions
    return {
      // Variables used in the template
      queryStore,
      detailsStore,
      DisplayDetails,
      DisplayFrequencies,
      DisplayConstraints,
      DisplayColumns,
      // Functions for activating/selecting columns
      selectDetailColumn,
      selectFrequencyColumn,
      selectConstraintColumn,
      selectDisplayColumns,
      // Functions used in ag-grid table
      defaultColDef,
      columnDefs,
      rowData,
      rowClassRules,
      onGridReady,
      onFirstDataRendered() {
        gridApi.value.sizeColumnsToFit()
      },
      sizeToFit() {
        gridApi.value.sizeColumnsToFit()
      },
      autoSizeAll() {
        const allColumnIds = []
        columnApi.value.getColumns().forEach((column) => {
          allColumnIds.push(column.getId())
        })
        columnApi.value.autoSizeColumns(allColumnIds)
      },
      onCellClicked(event) {
        if (
          !['selector', 'variant_icons', 'igv'].includes(
            event.column.getColId()
          )
        ) {
          $('#variantDetailsModal').modal()
          detailsStore.fetchVariantDetails(event, previousQueryDetails)
        }
      },
    }
  },
  mounted() {
    // TODO ? Maybe there is a better way to active selectpicker
    $('#result-columns-selector').selectpicker()
  },
}
</script>

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
