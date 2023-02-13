<script setup>
import { computed, onMounted, watch, ref } from 'vue'

import EasyDataTable from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'

import svsApi from '@svs/api/svs.js'
import { useSvFilterStore } from '@svs/stores/filterSvs.js'
import { formatLargeInt, displayName } from '@varfish/helpers.js'

const sortedList = (lst, unique = true) => {
  const tmp = unique ? new Set(lst) : lst
  const result = Array.from(tmp).filter((str) => str?.length)
  result.sort()
  return result
}

/** Define props. */
const props = defineProps({
  caseObj: Object,
})

/** Define emits. */
const emit = defineEmits([
  'variantSelected', // sv row clicked, arg is SvQueryResultRowRow UUID
])

// Handle click of row
const onShowDetailsClicked = (item) => {
  emit('variantSelected', item)
}

// Initialize filter query store.
const svFilterStore = useSvFilterStore()

// Headers for the table.
const _popWidth = 75
const tableHeaders = computed(() => {
  const result = [
    { text: 'Icons', value: 'icons', width: 50 },
    { text: 'Position', value: 'chrom-pos', width: 150, sortable: true },
    { text: 'Length', value: 'payload.sv_length', width: 50, sortable: true },
    { text: 'SV Type', value: 'sv_type', width: 100 },
    { text: 'Genes', value: 'genes', width: 200 },
    {
      text: 'In-House',
      value: 'payload.overlap_counts.inhouse',
      width: _popWidth,
      sortable: true,
    },
    {
      text: 'ExAC',
      value: 'payload.overlap_counts.exac',
      width: _popWidth,
      sortable: true,
    },
    {
      text: '1000G',
      value: 'payload.overlap_counts.g1k',
      width: _popWidth,
      sortable: true,
    },
    {
      text: 'gnomAD',
      value: 'payload.overlap_counts.gnomad',
      width: _popWidth,
      sortable: true,
    },
    {
      text: 'dbVar',
      value: 'payload.overlap_counts.dbvar',
      width: _popWidth,
      sortable: true,
    },
    {
      text: 'DGV',
      value: 'payload.overlap_counts.dgv',
      width: _popWidth,
      sortable: true,
    },
    {
      text: 'DGV GS',
      value: 'payload.overlap_counts.dgv_gs',
      width: _popWidth,
      sortable: true,
    },
    {
      text: 'TAD dist.',
      value: 'payload.tad_boundary_distance',
      width: 50,
      sortable: true,
    },
  ]
  for (const [index, row] of (props.caseObj?.pedigree || []).entries()) {
    result.push({
      text: displayName(row.name),
      value: `callInfos.${index}`,
    })
  }
  result.push({
    text: 'actions',
    value: 'actions',
    width: 100,
  })
  return result
})

const callInfosSlots = computed(() => {
  const result = {}
  for (let i = 0; i < (props.caseObj?.pedigree?.length ?? 0); i++) {
    result[`item-call-info.${i}`] = props.caseObj.pedigree[i].name
  }
  return result
})

/** Whether to display TAD genes. */
const showTadGenesEnabled = ref(false)
/** Rows to display in the table. */
const tableRows = ref([])
/** Selected table rows. */
const tableRowsSelected = ref([])
/** Whether the Vue3EasyDataTable is loading. */
const tableLoading = ref(false)
/** The table server options, updated by Vue3EasyDataTable. */
const tableServerOptions = ref({
  page: 1,
  rowsPerPage: 50,
  sortBy: 'chrom-pos',
  sortType: 'asc',
})

/** Return list of genes with symbol. */
const withSymbol = (lst) => {
  return lst.filter((elem) => elem.symbol)
}

/** Whether has tad genes and should display tad genes. */
const showTadGenes = (lst) => {
  return withSymbol(lst).length && showTadGenesEnabled.value
}

/** Return class name for the given gene. */
const geneClass = (gene, dangerClass, otherwiseClass = '') => {
  return gene.is_acmg || gene.is_disease_gene ? dangerClass : otherwiseClass
}

/** Return title for the given gene. */
const geneTitle = (gene) => {
  if (gene.is_acmg) {
    return 'Gene is in ACMG incidental findings list'
  } else if (gene.is_disease_gene) {
    return 'Gene is a known disease gene in OMIM'
  } else {
    return ''
  }
}

/** Load data from table as configured by tableServerOptions. */
const loadFromServer = async () => {
  const transmogrify = (row) => {
    row.chromosome = row.chromosome.startsWith('chr')
      ? row.chromosome
      : `chr${row.chromosome}`
    row.callInfos = (props.caseObj?.pedigree || []).map((member) => {
      return row.payload.call_info[member.name].genotype
    })
    return row
  }

  tableLoading.value = true
  const response = await svsApi.listSvQueryResultRow(
    svFilterStore.csrfToken,
    svFilterStore.queryResultSet.sodar_uuid,
    {
      pageNo: tableServerOptions.value.page,
      pageSize: tableServerOptions.value.rowsPerPage,
      orderBy:
        tableServerOptions.value.sortBy === 'chrom-pos'
          ? 'chromosome_no,start'
          : tableServerOptions.value.sortBy,
      orderDir: tableServerOptions.value.sortType,
    }
  )
  tableRows.value = response.results.map((row) => transmogrify(row))
  tableLoading.value = false
}

const goToLocus = async (release, chromosome, start, end) => {
  const chrPrefixed = chromosome.startsWith('chr')
    ? chromosome
    : `chr${chromosome}`
  await fetch(
    `http://127.0.0.1:60151/goto?locus=${chrPrefixed}:${start}-${end}`
  )
}

const ucscUrl = (release, chromosome, start, end) => {
  const db = release === 'GRCh37' ? 'hg19' : 'hg38'
  return `https://genome-euro.ucsc.edu/cgi-bin/hgTracks?db=${db}&position=${chromosome}:${start}-${end}`
}

const ensemblUrl = (release, chromosome, start, end) => {
  const subdomain = release === 'GRCh37' ? 'grch37' : 'www'
  return `https://${subdomain}.ensembl.org/Homo_sapiens/Location/View?r=${chromosome}:${start}-${end}`
}

const dgvUrl = (release, chromosome, start, end) => {
  const _ = release
  return `http://dgv.tcag.ca/gb2/gbrowse/dgv2_hg19/?name=${chromosome}:${start}-${end};search=Search`
}

const gnomadUrl = (release, chromosome, start, end) => {
  const _ = release
  return `https://gnomad.broadinstitute.org/region/${chromosome}-${start}-${end}`
}

const alertOnRefGt = (callInfo) => {
  if (
    (callInfo.gt == '0/0' || callInfo.gt == '0|0' || callInfo.gt == '0') &&
    (!!callInfo.paired_end_var || !!callInfo.split_read_var)
  ) {
    return true
  } else {
    return false
  }
}

/** Load data when mounted. */
onMounted(() => {
  loadFromServer()
})

/** Watch changes in tableServerOptions and reload if necessary. */
watch(
  tableServerOptions,
  (_newValue, _oldValue) => {
    loadFromServer()
  },
  { deep: true }
)
</script>

<template>
  <div class="card">
    <div class="card-header d-flex flex-row pt-1 pb-1">
      <div class="pr-3 align-self-start record-count">
        <div>
          <label class="font-weight-bold small mb-0 text-nowrap">
            # Records
          </label>
        </div>
        <div class="text-center">
          <span class="btn btn-sm btn-outline-secondary">
            {{ formatLargeInt(svFilterStore.queryResultSet.result_row_count) }}
          </span>
        </div>
      </div>
      <div class="pr-3 align-self-start record-count">
        <div>
          <label class="font-weight-bold small mb-0 text-nowrap">
            Query Time
          </label>
        </div>
        <div class="text-center">
          <span class="btn btn-sm btn-outline-secondary">
            {{ svFilterStore.queryResultSet.elapsed_seconds.toFixed(1) }}s
          </span>
        </div>
      </div>
      <div class="pr-3 align-self-start">
        <div>
          <label
            class="font-weight-bold small mb-0 text-nowrap"
            for="tad-gene-checkbox"
          >
            TAD Genes
          </label>
        </div>
        <div class="">
          <label
            class="btn btn-sm btn-outline-secondary"
            for="tad-gene-checkbox"
          >
            <div class="custom-control custom-checkbox">
              <input
                type="checkbox"
                class="custom-control-input"
                id="tad-gene-checkbox"
                v-model="showTadGenesEnabled"
              />
              <label for="tad-gene-checkbox" class="custom-control-label"
                >show</label
              >
            </div>
          </label>
        </div>
      </div>
    </div>
    <EasyDataTable
      v-model:items-selected="tableRowsSelected"
      v-model:server-options="tableServerOptions"
      table-class-name="customize-table"
      :loading="tableLoading"
      :server-items-length="svFilterStore.queryResultSet.result_row_count"
      :headers="tableHeaders"
      :items="tableRows"
      :rows-items="[20, 50, 200, 1000]"
      alternating
      buttons-pagination
      show-index
    >
      <template #item-icons="{ payload }">
        <div class="text-nowrap">
          <!-- flags -->
          <i-fa-solid-bookmark
            v-if="payload.flag_count"
            class="text-muted"
            title="flags & bookmarks"
          />
          <i-fa-regular-bookmark
            v-else
            class="text-muted icon-inactive"
            title="flags & bookmarks"
          />
          <!-- comments -->
          <i-fa-solid-comment
            v-if="payload.comment_count"
            class="text-muted ml-1"
          />
          <i-fa-regular-comment v-else class="text-muted icon-inactive ml-1" />
          <!-- tool -->
          <span :title="payload.caller">
            <i-fa-solid-car class="text-muted ml-1" />
          </span>
        </div>
      </template>

      <template
        #item-chrom-pos="{
          chromosome,
          start,
          payload: {
            masked_breakpoints: { repeat, segdup },
          },
        }"
      >
        {{ chromosome }}:{{ formatLargeInt(start) }}
        <span
          v-if="repeat > 0 || segdup > 0"
          class="text-danger"
          :title="`Breakpoints overlap with repetitive sequence (repeats: ${repeat}, segmental duplications: ${segdup}). Such calls are not reliable for short-read data.`"
        >
          <i-mdi-alert-box />
        </span>
      </template>

      <template
        #item-genes="{
          payload: {
            ovl_genes,
            tad_genes,
            ovl_disease_gene,
            tad_disease_gene,
            clinvar_ovl_vcvs,
            known_pathogenic,
          },
        }"
      >
        <template
          v-if="withSymbol(ovl_genes).length || showTadGenes(tad_genes)"
        >
          <template v-for="(item, index) in withSymbol(ovl_genes)">
            <span v-if="index > 0">, </span>
            <span
              class="text-nowrap"
              :class="geneClass(item, 'text-danger')"
              :title="geneTitle(item)"
            >
              {{ item.symbol }}
              <i-mdi-alert-box v-if="item.is_disease_gene || item.is_acmg"
            /></span>
          </template>
          <span
            v-if="withSymbol(ovl_genes).length && showTadGenes(tad_genes)"
            class="text-muted"
            >,
          </span>
          <template v-if="showTadGenes(tad_genes)">
            <template v-for="(item, index) in withSymbol(tad_genes)">
              <span class="text-muted" v-if="index > 0">, </span>
              <span
                class="font-italic text-nowrap"
                :class="geneClass(item, 'text-info', 'text-muted')"
                :title="geneTitle(item)"
              >
                {{ item.symbol }}
                <i-mdi-alert-box v-if="item.is_disease_gene || item.is_acmg" />
              </span>
            </template>
          </template>
        </template>
        <template v-else> &mdash; </template>
        <span
          v-if="withSymbol(tad_genes).length && !showTadGenes(tad_genes)"
          class="text-muted font-italic"
        >
          <template v-if="withSymbol(ovl_genes).length"> +</template>
          {{ withSymbol(tad_genes).length }} in TAD
          <template v-if="tad_disease_gene">
            <span
              title="Overlapping TAD contains disease gene!"
              class="text-info"
            >
              <i-mdi-alert-box />
            </span>
          </template>
        </span>
      </template>

      <template #item-sv_type="{ sv_type, payload }">
        <span
          :class="{
            'text-danger':
              payload.clinvar_ovl_vcvs.length ||
              payload.known_pathogenic.length,
          }"
        >
          {{ sv_type }}
          <template v-if="payload.clinvar_ovl_vcvs.length">
            <span
              :title="`Overlapping ClinVar SVs: ${payload.clinvar_ovl_vcvs}`"
              class="text-danger"
            >
              <i-mdi-hospital-building />
            </span>
          </template>
          <template v-if="payload.known_pathogenic.length">
            <span
              :title="`Overlapping with known pathogenic variant(s): ${payload.known_pathogenic
                .map((elem) => elem.id)
                .join(', ')}`"
              class="text-danger"
            >
              <i-mdi-lightning-bolt />
            </span>
          </template>
        </span>
      </template>

      <template #item-payload.sv_length="{ payload }">
        <div class="text-right text-nowrap space">
          {{ formatLargeInt(payload.sv_length) }}
          <span class="text-muted">bp</span>
        </div>
      </template>

      <template #item-payload.overlap_counts.exac="{ payload }">
        <div class="text-right text-nowrap space">
          {{ formatLargeInt(payload.overlap_counts.exac) }}
        </div>
      </template>
      <template #item-payload.overlap_counts.g1k="{ payload }">
        <div class="text-right text-nowrap space">
          {{ formatLargeInt(payload.overlap_counts.g1k) }}
        </div>
      </template>
      <template #item-payload.overlap_counts.gnomad="{ payload }">
        <div class="text-right text-nowrap space">
          {{ formatLargeInt(payload.overlap_counts.gnomad) }}
        </div>
      </template>
      <template #item-payload.overlap_counts.dgv="{ payload }">
        <div class="text-right text-nowrap space">
          {{ formatLargeInt(payload.overlap_counts.dgv) }}
        </div>
      </template>
      <template #item-payload.overlap_counts.dbvar="{ payload }">
        <div class="text-right text-nowrap space">
          {{ formatLargeInt(payload.overlap_counts.dbvar) }}
        </div>
      </template>
      <template #item-payload.overlap_counts.dgv_gs="{ payload }">
        <div class="text-right text-nowrap space">
          {{ formatLargeInt(payload.overlap_counts.dgv_gs) }}
        </div>
      </template>

      <template #item-actions="svRecord">
        <div class="btn-group sodar-list-btn-group">
          <button
            @click.prevent="onShowDetailsClicked(svRecord)"
            type="button"
            title="Show SV Details"
            class="btn sodar-list-btn btn-primary"
          >
            <i-mdi-eye />
            Details
          </button>
          <button
            @click.prevent="
              goToLocus(
                svRecord.payload.release,
                svRecord.payload.chromosome,
                svRecord.payload.start,
                svRecord.payload.end
              )
            "
            type="button"
            title="Go to locus in IGV"
            class="btn sodar-list-btn btn-primary"
          >
            IGV
          </button>
          <button
            type="button"
            class="btn btn-primary dropdown-toggle dropdown-toggle-split sodar-list-dropdown"
            data-toggle="dropdown"
          >
            <span class="sr-only">Toggle Dropdown</span>
          </button>
          <div class="dropdown-menu dropdown-menu-right" style="z-index: 1030">
            <a
              class="dropdown-item"
              :href="
                ucscUrl(
                  svRecord.payload.release,
                  svRecord.payload.chromosome,
                  svRecord.payload.start,
                  svRecord.payload.end
                )
              "
              target="_blank"
            >
              Locus @UCSC
            </a>
            <a
              class="dropdown-item"
              :href="
                ensemblUrl(
                  svRecord.payload.release,
                  svRecord.payload.chromosome,
                  svRecord.payload.start,
                  svRecord.payload.end
                )
              "
              target="_blank"
            >
              Locus @EnsEMBL
            </a>
            <a
              class="dropdown-item"
              :href="
                dgvUrl(
                  svRecord.payload.release,
                  svRecord.payload.chromosome,
                  svRecord.payload.start,
                  svRecord.payload.end
                )
              "
              target="_blank"
              v-if="svRecord.payload.release === 'GRCh37'"
            >
              Locus @DGV
            </a>
            <a class="disabled" href="#" v-else>
              <!-- not for GRCh38 yet -->
              Locus @DGV
            </a>
            <a
              class="dropdown-item"
              :href="
                gnomadUrl(
                  svRecord.payload.release,
                  svRecord.payload.chromosome,
                  svRecord.payload.start,
                  svRecord.payload.end
                )
              "
              target="_blank"
              v-if="svRecord.payload.release === 'GRCh37'"
            >
              Locus @gnomAD
            </a>
            <a class="disabled" href="#" v-else>
              <!-- not for GRCh38 yet -->
              Locus @gnomAD
            </a>
          </div>
        </div>
      </template>

      <template
        #[callInfoSlot]="{ payload: { call_info } }"
        v-for="(name, callInfoSlot) of callInfosSlots"
      >
        <div
          class="text-center text-nowrap"
          :class="{ 'text-danger': alertOnRefGt(call_info[name]) }"
        >
          <span :title="JSON.stringify(call_info[name])">
            {{ call_info[name].genotype }}
          </span>

          <span
            v-if="alertOnRefGt(call_info[name])"
            title="REF genotype but variant evidence!"
          >
            <i-mdi-alert-box />
          </span>
        </div>
      </template>

      <template #item-payload.tad_boundary_distance="{ payload }">
        <div
          v-if="payload.tad_boundary_distance === null"
          class="text-nowrap text-center"
        >
          <span class="small text-muted"> &geq;10kbp </span>
        </div>
        <div v-else class="text-nowrap text-right">
          {{ formatLargeInt(payload.tad_boundary_distance) }}
          <span class="text-muted">bp</span>
        </div>
      </template>
    </EasyDataTable>
  </div>
</template>

<style>
.customize-table {
  --easy-table-border: none;
  /*--easy-table-header-background-color: #2d3a4f;*/
}
</style>
