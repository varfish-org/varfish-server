<script setup>
import { LinearStrucvarImpl } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { sortBy } from 'sort-by-typescript'
import { computed, onBeforeMount, reactive, ref, watch } from 'vue'
import EasyDataTable from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'

import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { SvClient } from '@/svs/api/strucvarClient'
import { emptyFlagsTemplate, useSvFlagsStore } from '@/svs/stores/strucvarFlags'
import { useSvAcmgRatingStore } from '@/svs/stores/svAcmgRating'
import { useSvCommentsStore } from '@/svs/stores/svComments'
import { useSvQueryStore } from '@/svs/stores/svQuery'
import { useSvResultSetStore } from '@/svs/stores/svResultSet'
import { displayName, formatLargeInt } from '@/varfish/helpers'
import { useCtxStore } from '@/varfish/stores/ctx'
import { getAcmgBadge } from '@/variants/helpers'

const MAX_GENES = 20

/** Define emits. */
const emit = defineEmits(['variantSelected'])

const showVariantDetails = (sodarUuid, section) => {
  svResultSetStore.lastVisited = sodarUuid
  emit('variantSelected', {
    svresultrow: sodarUuid,
    selectedSection: section ?? 'gene-overview',
  })
}

const scrollToLastPosition = () => {
  if (svQueryStore.lastPosition) {
    const elem = document.querySelector('div#app')
    if (elem) {
      elem.scrollTop = svQueryStore.lastPosition
    }
  }
}

// Initialize stores
const ctxStore = useCtxStore()
const caseDetailsStore = useCaseDetailsStore()
const svResultSetStore = useSvResultSetStore()
const svFlagsStore = useSvFlagsStore()
const svCommentsStore = useSvCommentsStore()
const svAcmgRatingStore = useSvAcmgRatingStore()
const svQueryStore = useSvQueryStore()

// Headers for the table.
const _popWidth = 75
const tableHeaders = computed(() => {
  const result = [
    { text: 'Icons', value: 'icons', width: 50 },
    { text: 'Position', value: 'chrom-pos', width: 150, sortable: true },
    { text: 'Length', value: 'payload.sv_length', width: 50, sortable: true },
    { text: 'Type', value: 'sv_type', width: 50 },
    { text: 'Genes', value: 'genes' },
    {
      text: 'in-house frequency',
      value: 'payload.overlap_counts.inhouse',
      width: 50,
      sortable: true,
    },
    {
      text: 'gnomAD exomes',
      value: 'payload.overlap_counts.gnomad_exomes',
      width: 50,
      sortable: true,
    },
    {
      text: 'gnomAD genomes',
      value: 'payload.overlap_counts.gnomad_genomes',
      width: 50,
      sortable: true,
    },
  ]
  for (const [index, row] of (
    caseDetailsStore.caseObj?.pedigree || []
  ).entries()) {
    result.push({
      text: displayName(row.name),
      value: `callInfo.${index}`,
      width: 50,
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
  for (let i = 0; i < (caseDetailsStore.caseObj?.pedigree?.length ?? 0); i++) {
    result[`item-callInfo.${i}`] = caseDetailsStore.caseObj.pedigree[i].name
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
/** Reactive key to force table re-render when flags change */
const tableKey = ref(0)
/** The table server options, updated by Vue3EasyDataTable. */
const tableServerOptions = computed({
  get() {
    return reactive({
      page: svResultSetStore.tablePageNo || 1,
      rowsPerPage: svResultSetStore.tablePageSize || 50,
      sortBy: svResultSetStore.tableSortBy || 'chrom-pos',
      sortType: svResultSetStore.tableSortType || 'asc',
    })
  },
  set(options) {
    svResultSetStore.tablePageNo = options.page
    svResultSetStore.tablePageSize = options.rowsPerPage
    svResultSetStore.tableSortBy = options.sortBy
    svResultSetStore.tableSortType = options.sortType
  },
})

/** Return list of genes with symbol. */
const withSymbol = (lst) => {
  return lst.filter((elem) => {
    return elem.gene?.symbol ?? elem.symbol
  })
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

/** Check if a variant has flags */
const hasFlags = (item) => {
  const result = svFlagsStore.getFlags?.(item)
  return !!result
}

/** Load data from table as configured by tableServerOptions. */
const loadFromServer = async () => {
  const sortGene = (genes) => {
    if (genes.length === 0) {
      return genes
    } else if (genes[0].gene) {
      return genes.toSorted(
        sortBy('-gene.is_acmg', '-gene.is_disease_gene', 'gene.symbol'),
      )
    } else {
      return genes.toSorted(sortBy('-is_acmg', '-is_disease_gene', 'symbol'))
    }
  }

  const transmogrify = (row) => {
    row.chromosome = row.chromosome.startsWith('chr')
      ? row.chromosome.slice(3)
      : row.chromosome
    row.callInfos = (caseDetailsStore.caseObj?.pedigree || []).map((member) => {
      return row.payload.call_info[member.name].genotype
    })
    if (!('masked_breakpoints' in row.payload)) {
      row.payload.masked_breakpoints = { repeat: null, segdup: null }
    }
    if (row.payload.ovl_genes) {
      row.payload.ovl_genes = sortGene(row.payload.ovl_genes)
    }
    if (row.payload.tad_genes) {
      row.payload.tad_genes = sortGene(row.payload.tad_genes)
    }
    if (row.payload.tx_effects) {
      row.payload.tx_effects = sortGene(row.payload.tx_effects)
    }
    return row
  }

  tableLoading.value = true
  const svClient = new SvClient(ctxStore.csrfToken)
  if (svResultSetStore.resultSetUuid) {
    const response = await svClient.listSvQueryResultRow(
      svResultSetStore.resultSetUuid,
      {
        pageNo: tableServerOptions.value.page,
        pageSize: tableServerOptions.value.rowsPerPage,
        orderBy:
          tableServerOptions.value.sortBy === 'chrom-pos'
            ? 'chromosome_no,start'
            : tableServerOptions.value.sortBy,
        orderDir: tableServerOptions.value.sortType,
      },
    )
    tableRows.value = response.results.map((row) => transmogrify(row))
    tableLoading.value = false
  }
}

const goToLocus = async ({ chromosome, start, end }) => {
  const chrom = chromosome == 'chrMT' ? 'chrM' : chromosome
  await fetch(`http://127.0.0.1:60151/goto?locus=${chrom}:${start}-${end}`)
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
    (callInfo.effective_genotype === 'ref' ||
      callInfo.effective_genotype === 'non-variant') &&
    (!!callInfo.paired_end_var || !!callInfo.split_read_var)
  ) {
    return true
  } else {
    return false
  }
}

// Flag the given SV record as visual artifact.
const flagAsArtifact = async (svRecord) => {
  await svFlagsStore.retrieveFlags(svRecord)
  if (svFlagsStore.flags) {
    // update existing flags
    const flags = {
      ...svFlagsStore.flags,
      flag_summary: 'negative',
      flag_visual: 'negative',
    }
    await svFlagsStore.updateFlags(flags)
  } else {
    // create new flags
    const flags = {
      ...emptyFlagsTemplate,
      flag_summary: 'negative',
      flag_visual: 'negative',
    }
    await svFlagsStore.createFlags(svRecord, flags)
  }
}

const getAcmgRating = (payload) => {
  return svAcmgRatingStore.getAcmgRating(
    new LinearStrucvarImpl(
      payload.sv_type,
      payload.release === 'GRCh37' ? 'grch37' : 'grch38',
      payload.chromosome,
      payload.start,
      payload.end,
      payload.sv_type,
    ),
  )
}

const getAcmgBadgeClasses = (acmgClass) => {
  const acmgBadgeClasses = ['ml-1', 'badge', getAcmgBadge(acmgClass)]
  if (!acmgClass) {
    acmgBadgeClasses.push('badge-outline')
  }
  return acmgBadgeClasses.join(' ')
}

/** Return class name for table row. */
const tableRowClassName = (item, _rowNumber) => {
  if (item.sodar_uuid === svResultSetStore.lastVisited) {
    return 'last-visited-row'
  }
  if (!svFlagsStore.caseFlags) {
    return ''
  }
  const flagColors = ['positive', 'uncertain', 'negative']
  const flags = svFlagsStore.getFlags(item)
  if (!flags) {
    return ''
  }
  if (flagColors.includes(flags.flag_summary)) {
    return `${flags.flag_summary}-row`
  }
  const isBookmarked =
    flagColors.includes(flags.flag_visual) ||
    flagColors.includes(flags.flag_validation) ||
    flagColors.includes(flags.flag_molecular) ||
    flagColors.includes(flags.flag_phenotype_match) ||
    flags.flag_candidate ||
    flags.flag_doesnt_segregate ||
    flags.flag_final_causative ||
    flags.flag_for_validation ||
    flags.flag_no_disease_association ||
    flags.flag_segregates
  return isBookmarked ? 'bookmarked-row' : ''
}

onBeforeMount(async () => {
  if (svResultSetStore.resultSetUuid) {
    await loadFromServer()
    scrollToLastPosition()
  }
})

/** Update display when pagination or sorting changed. */
watch(
  [
    () => tableServerOptions.value.page,
    () => tableServerOptions.value.rowsPerPage,
    () => tableServerOptions.value.sortBy,
    () => tableServerOptions.value.sortType,
  ],
  async (
    [_newPageNo, _newRowsPerPage, _newSortBy, _newSortType],
    [_oldPageNo, _oldRowsPerPage, _oldSortBy, _oldSortType],
  ) => {
    await loadFromServer()
  },
)

watch(
  () => svResultSetStore.resultSetUuid,
  async (_newValue, _oldValue) => {
    if (_newValue) {
      await loadFromServer()
      scrollToLastPosition()
    }
  },
  { deep: true },
)

// Watch for changes in flags store state to trigger table re-render
watch(
  () => svFlagsStore.storeState.state,
  async (newState, oldState) => {
    if (newState === 'active' && oldState === 'fetching') {
      if (svResultSetStore.resultSetUuid) {
        tableKey.value += 1
        await loadFromServer()
      }
    }
  },
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
            {{ formatLargeInt(svResultSetStore?.resultSet?.result_row_count) }}
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
            {{ svResultSetStore?.resultSet?.elapsed_seconds?.toFixed(1) }}s
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
                id="tad-gene-checkbox"
                v-model="showTadGenesEnabled"
                type="checkbox"
                class="custom-control-input"
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
      :key="tableKey"
      v-model:items-selected="tableRowsSelected"
      v-model:server-options="tableServerOptions"
      table-class-name="customize-table"
      :loading="tableLoading"
      :server-items-length="svResultSetStore?.resultSet?.result_row_count"
      :body-row-class-name="tableRowClassName"
      :headers="tableHeaders"
      :items="tableRows"
      :rows-items="[20, 50, 200, 1000]"
      theme-color="#6c757d"
      buttons-pagination
      show-index
    >
      <template #empty-message>
        <em class="ml-2 text-dark" style="font-size: 150%">
          <strong>No variant passed the current filter settings.</strong><br />
          Please try relaxing your settings.
        </em>
      </template>
      <template #[`header-payload.overlap_counts.inhouse`]="header">
        <div :title="header.text">
          <i-mdi-house />
        </div>
      </template>
      <template #[`header-payload.overlap_counts.gnomad`]="header">
        <div :title="header.text">
          <i-mdi-earth />
        </div>
      </template>

      <template
        #item-icons="{
          sodar_uuid,
          release,
          chromosome,
          start,
          end,
          sv_type,
          payload,
        }"
      >
        <div class="text-nowrap">
          <i-fa-solid-search
            class="text-muted"
            role="button"
            @click.prevent="showVariantDetails(sodar_uuid, 'strucvar-genes')"
          />
          <i-fa-solid-bookmark
            v-if="hasFlags({ chromosome, start, end, sv_type })"
            :class="`${svFlagsStore.hasProjectWideFlags({ chromosome, start, end, sv_type }) ? 'text-warning' : 'text-muted'}`"
            title="flags & bookmarks"
            role="button"
            @click="showVariantDetails(sodar_uuid, 'strucvar-flags')"
          />
          <i-fa-regular-bookmark
            v-else
            :class="`${svFlagsStore.hasProjectWideFlags({ chromosome, start, end, sv_type }) ? 'text-warning' : 'text-muted'} icon-inactive`"
            title="flags & bookmarks"
            role="button"
            @click="showVariantDetails(sodar_uuid, 'strucvar-flags')"
          />
          <!-- comments -->
          <i-fa-solid-comment
            v-if="
              svCommentsStore.hasComment({
                chrom: chromosome,
                start: start,
                stop: end,
                svType: sv_type,
              })
            "
            :class="`${svCommentsStore.hasProjectWideComments({ chromosome, start, end, sv_type }) ? 'text-warning' : 'text-muted'} ml-1`"
            role="button"
            @click="showVariantDetails(sodar_uuid, 'strucvar-comments')"
          />
          <i-fa-regular-comment
            v-else
            :class="`${svCommentsStore.hasProjectWideComments({ chromosome, start, end, sv_type }) ? 'text-warning' : 'text-muted'} icon-inactive ml-1`"
            role="button"
            @click="showVariantDetails(sodar_uuid, 'strucvar-comments')"
          />
          <span
            title="ACMG rating"
            :class="
              getAcmgBadgeClasses(
                getAcmgRating({ release, chromosome, start, end, sv_type }),
              )
            "
            role="button"
            @click="showVariantDetails(sodar_uuid, 'strucvar-acmgrating')"
            >{{
              getAcmgRating({ release, chromosome, start, end, sv_type }) || '-'
            }}</span
          >
          <!-- tool -->
          <span :title="payload.caller">
            <i-fa-solid-car class="text-muted ml-1" />
          </span>
        </div>
      </template>

      <template
        #item-chrom-pos="{
          sodar_uuid,
          chromosome,
          start,
          payload: {
            masked_breakpoints: { repeat, segdup },
          },
        }"
      >
        <div
          role="button"
          @click="showVariantDetails(sodar_uuid, 'strucvar-genomebrowser')"
        >
          chr{{ chromosome }}:{{ formatLargeInt(start) }}
          <span
            v-if="repeat > 0 || segdup > 0"
            class="text-info"
            :title="`Breakpoints overlap with repetitive sequence (repeats: ${repeat}, segmental duplications: ${segdup}). Such calls are not reliable for short-read data.`"
          >
            <i-mdi-line-scan />
          </span>
        </div>
      </template>

      <template
        #item-genes="{
          sodar_uuid,
          payload: {
            ovl_genes,
            tad_genes,
            ovl_disease_gene,
            tad_disease_gene,
            tx_effects,
            clinvar_ovl_rcvs,
            known_pathogenic,
          },
        }"
      >
        <div
          role="button"
          @click="showVariantDetails(sodar_uuid, 'strucvar-calldetails')"
        >
          <template v-if="tx_effects.length || showTadGenes(tad_genes)">
            <template v-for="(item, index) in tx_effects.slice(0, MAX_GENES)">
              <span
                class="text-nowrap"
                :class="geneClass(item.gene, 'text-danger')"
                :title="geneTitle(item.gene)"
              >
                <template
                  v-if="
                    (item.transcript_effects ?? []).includes(
                      'transcript_variant',
                    )
                  "
                >
                  <span
                    class="badge badge-danger"
                    title="whole transcript is affected"
                    >tx</span
                  >
                </template>
                <template
                  v-else-if="
                    (item.transcript_effects ?? []).includes('exon_variant')
                  "
                >
                  <span class="badge badge-danger" title="exonic for gene"
                    >ex</span
                  >
                </template>
                <template
                  v-else-if="
                    (item.transcript_effects ?? []).includes(
                      'splice_region_variant',
                    )
                  "
                >
                  <span
                    class="badge badge-danger"
                    title="splice region for gene"
                    >sr</span
                  >
                </template>
                <template
                  v-else-if="
                    (item.transcript_effects ?? []).includes('intron_variant')
                  "
                >
                  <span class="badge badge-warning" title="intronic for gene"
                    >in</span
                  >
                </template>
                <template
                  v-else-if="
                    (item.transcript_effects ?? []).includes('upstream_variant')
                  "
                >
                  <span class="badge badge-secondary" title="upstream of gene"
                    >up</span
                  >
                </template>
                <template
                  v-else-if="
                    (item.transcript_effects ?? []).includes(
                      'downstream_variant',
                    )
                  "
                >
                  <span class="badge badge-secondary" title="downstream of gene"
                    >dw</span
                  >
                </template>
                {{ item.gene.symbol
                }}<span v-if="item.gene.is_disease_gene || item.gene.is_acmg">
                  <i-mdi-hospital-box /></span></span
              ><span v-if="index + 1 < Math.min(MAX_GENES, tx_effects.length)"
                >,
              </span>
            </template>
            <template v-if="tx_effects.length > MAX_GENES">
              + {{ tx_effects.length - MAX_GENES }} genes
            </template>
            <span
              v-if="tx_effects.length && showTadGenes(tad_genes)"
              class="text-muted"
              >,
            </span>
            <template v-if="showTadGenes(tad_genes)">
              <template v-for="(item, index) in withSymbol(tad_genes)">
                <span v-if="index > 0" class="text-muted">, </span>
                <span
                  class="font-italic text-nowrap"
                  :class="geneClass(item, 'text-info', 'text-muted')"
                  :title="geneTitle(item)"
                >
                  {{ item.symbol }}
                  <i-mdi-hospital-box
                    v-if="item.is_disease_gene || item.is_acmg"
                  />
                </span>
              </template>
            </template>
          </template>
          <template v-else> &mdash; </template>
          <span
            v-if="withSymbol(tad_genes).length && !showTadGenes(tad_genes)"
            class="text-muted font-italic"
          >
            <template v-if="tx_effects.length"> +</template>
            {{ withSymbol(tad_genes).length }} in TAD
            <template v-if="tad_disease_gene">
              <span
                title="Overlapping TAD contains disease gene!"
                class="text-info"
              >
                <i-mdi-hospital-box />
              </span>
            </template>
          </span>
        </div>
      </template>

      <template #item-sv_type="{ sv_type, payload }">
        <span
          class="text-nowrap"
          :class="{
            'text-danger': payload.clinvar_ovl_rcvs.length,
            // || payload.known_pathogenic.length
          }"
        >
          {{ sv_type }}
          <template v-if="payload.clinvar_ovl_rcvs.length">
            <span
              :title="`Overlapping ClinVar SVs: ${payload.clinvar_ovl_rcvs}`"
              class="text-danger"
            >
              <i-mdi-hospital-building />
            </span>
          </template>
          <!-- <template v-if="payload.known_pathogenic.length">
            <span
              :title="`Overlapping with known pathogenic variant(s): ${payload.known_pathogenic
                .map((elem) => elem.id)
                .join(', ')}`"
              class="text-danger"
            >
              <i-mdi-lightning-bolt />
            </span>
          </template> -->
        </span>
      </template>

      <template #item-payload.sv_length="{ sodar_uuid, payload }">
        <div
          class="text-right text-nowrap space"
          role="button"
          @click="showVariantDetails(sodar_uuid, 'strucvar-genomebrowser')"
        >
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
      <template #item-payload.overlap_counts.gnomad_exomes="{ payload }">
        <div class="text-right text-nowrap space">
          {{ formatLargeInt(payload.overlap_counts.gnomad_exomes) }}
        </div>
      </template>
      <template #item-payload.overlap_counts.gnomad_genomes="{ payload }">
        <div class="text-right text-nowrap space">
          {{ formatLargeInt(payload.overlap_counts.gnomad_genomes) }}
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
            type="button"
            title="Go to locus in IGV"
            class="btn sodar-list-btn btn-primary"
            @click.prevent="goToLocus(svRecord)"
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
                  svRecord.release,
                  `chr${svRecord.chromosome}`,
                  svRecord.start,
                  svRecord.end,
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
                  svRecord.release,
                  `chr${svRecord.chromosome}`,
                  svRecord.start,
                  svRecord.end,
                )
              "
              target="_blank"
            >
              Locus @EnsEMBL
            </a>
            <a
              v-if="svRecord.release === 'GRCh37'"
              class="dropdown-item"
              :href="
                dgvUrl(
                  svRecord.release,
                  `chr${svRecord.chromosome}`,
                  svRecord.start,
                  svRecord.end,
                )
              "
              target="_blank"
            >
              Locus @DGV
            </a>
            <a v-else class="dropdown-item disabled" href="#">
              <!-- not for GRCh38 yet -->
              Locus @DGV
            </a>
            <a
              v-if="svRecord.release === 'GRCh37'"
              class="dropdown-item"
              :href="
                gnomadUrl(
                  svRecord.release,
                  `chr${svRecord.chromosome}`,
                  svRecord.start,
                  svRecord.end,
                )
              "
              target="_blank"
            >
              Locus @gnomAD
            </a>
            <a v-else class="dropdown-item disabled" href="#">
              <!-- not for GRCh38 yet -->
              Locus @gnomAD
            </a>
            <div class="dropdown-divider"></div>
            <a
              class="dropdown-item"
              href="#"
              @click.prevent="flagAsArtifact(svRecord)"
            >
              <i-mdi-eye-minus />
              Flag as Artifact
            </a>
          </div>
        </div>
      </template>

      <template
        v-for="(name, callInfoSlot) in callInfosSlots"
        #[callInfoSlot]="{ payload: { call_info } }"
      >
        <div
          class="text-center text-nowrap"
          :class="{ 'text-danger': alertOnRefGt(call_info[name]) }"
        >
          {{ call_info[name].genotype }}
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
  --easy-table-row-border: none;
}

.positive-row {
  --easy-table-body-row-background-color: #f5c6cb;
}

.uncertain-row {
  --easy-table-body-row-background-color: #ffeeba;
}

.negative-row {
  --easy-table-body-row-background-color: #c3e6cb;
}

.bookmarked-row {
  --easy-table-body-row-background-color: #cccccc;
}
.last-visited-row {
  --easy-table-body-row-background-color: #85c1e9;
}
</style>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
