<script setup>
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { SeqvarImpl } from '@bihealth/reev-frontend-lib/lib/genomicVars'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import $ from 'jquery'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import EasyDataTable from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'

import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import {
  displayName,
  formatFloat,
  formatLargeInt,
  truncateText,
} from '@/varfish/helpers'
import { useCtxStore } from '@/varfish/stores/ctx'
import { VariantClient } from '@/variants/api/variantClient'
import ColumnControl from '@/variants/components/ColumnControl.vue'
import ExportResults from '@/variants/components/ExportResults.vue'
import {
  DisplayColumns,
  DisplayColumnsToText,
  DisplayConstraints,
  DisplayDetails,
  DisplayFrequencies,
} from '@/variants/enums'
import { getAcmgBadge } from '@/variants/helpers'
import { copy } from '@/variants/helpers'
import { useVariantAcmgRatingStore } from '@/variants/stores/variantAcmgRating'
import { useVariantCommentsStore } from '@/variants/stores/variantComments'
import { useVariantFlagsStore } from '@/variants/stores/variantFlags'
import { useVariantQueryStore } from '@/variants/stores/variantQuery'
import { useVariantResultSetStore } from '@/variants/stores/variantResultSet'

/**
 * The component's props.
 */
const props = defineProps({
  /** The pathogenicity score enabled. */
  pathoEnabled: Boolean,
  /** The phenotype score enabled. */
  prioEnabled: Boolean,
  /** The GestaltMatcher score enabled. */
  gmEnabled: Boolean,
  /** The PEDIA score enabled. */
  pediaEnabled: Boolean,
})

/**
 * Define the emitted events.
 */
const emit = defineEmits([
  /** Variant has been selected. */
  'variantSelected',
])

/**
 * Setup stores before mounting the component.
 */
const ctxStore = useCtxStore()
const caseDetailsStore = useCaseDetailsStore()
const flagsStore = useVariantFlagsStore()
const commentsStore = useVariantCommentsStore()
const acmgRatingStore = useVariantAcmgRatingStore()
const variantResultSetStore = useVariantResultSetStore()
const variantQueryStore = useVariantQueryStore()

/** The details columns to show. */
const displayDetails = computed({
  get() {
    return (
      variantResultSetStore.displayDetails || DisplayDetails.Coordinates.value
    )
  },
  set(newValue) {
    variantResultSetStore.displayDetails = newValue
  },
})

/** The frequency columns to show. */
const displayFrequency = computed({
  get() {
    return (
      variantResultSetStore.displayFrequency ||
      DisplayFrequencies.GnomadExomes.value
    )
  },
  set(newValue) {
    variantResultSetStore.displayFrequency = newValue
  },
})

/** The constraint columns to show. */
const displayConstraint = computed({
  get() {
    return (
      variantResultSetStore.displayConstraint ||
      DisplayConstraints.GnomadPli.value
    )
  },
  set(newValue) {
    variantResultSetStore.displayConstraint = newValue
  },
})

/** The additional columns to display. */
const displayColumns = computed({
  get() {
    return variantResultSetStore.displayColumns ?? [DisplayColumns.Effect.value]
  },
  set(newValue) {
    variantResultSetStore.displayColumns = newValue
  },
})

/** The table server options, updated by Vue3EasyDataTable. */
const tableServerOptions = computed({
  get() {
    return reactive({
      page: variantResultSetStore.tablePageNo || 1,
      rowsPerPage: variantResultSetStore.tablePageSize || 50,
      sortBy: variantResultSetStore.tableSortBy || 'position',
      sortType: variantResultSetStore.tableSortType || 'asc',
    })
  },
  set(options) {
    variantResultSetStore.tablePageNo = options.page
    variantResultSetStore.tablePageSize = options.rowsPerPage
    variantResultSetStore.tableSortBy = options.sortBy
    variantResultSetStore.tableSortType = options.sortType
  },
})

/**
 * Setup for easy-data-table.
 */

const coordinatesClinvarColumns = () => {
  if (displayDetails.value === DisplayDetails.Clinvar.value) {
    return [{ text: 'clinvar summary', value: 'clinvar' }]
  }
  return [
    { text: 'position', value: 'position', sortable: true },
    { text: 'ref', value: 'reference', sortable: true },
    { text: 'alt', value: 'alternative', sortable: true },
  ]
}

const optionalColumns = () => {
  const optionalColumnTexts = copy(DisplayColumnsToText)
  for (const { field, label } of extraAnnoFields.value) {
    optionalColumnTexts[`extra_anno${field}`] = label
  }
  return displayColumns.value.map((field) => ({
    text: optionalColumnTexts[field],
    value: field,
    sortable: field.startsWith('extra_anno'),
  }))
}

const genotypeColumns = () => {
  if (!caseDetailsStore.caseObj) {
    return []
  }
  return Object.entries(caseDetailsStore.genotypeMapping).map(
    ([value, textData]) => {
      return {
        text: textData.displayName,
        value: value,
        sortable: true,
      }
    },
  )
}

const scoreColumns = () => {
  let data = []
  if (props.pathoEnabled) {
    data = [
      {
        text: 'patho score',
        value: 'pathogenicity_score',
        sortable: true,
      },
    ]
  }
  if (props.prioEnabled) {
    data = [
      ...data,
      {
        text: 'pheno score',
        value: 'phenotype_score',
        sortable: true,
      },
    ]
  }
  if (props.pathoEnabled && props.prioEnabled) {
    data = [
      ...data,
      {
        text: 'patho+pheno score',
        value: 'patho_pheno_score',
        sortable: true,
      },
    ]
  }
  if (props.gmEnabled) {
    data = [
      ...data,
      {
        text: 'Gestalt score',
        value: 'gm_score',
        sortable: true,
      },
    ]
  }
  if (props.pediaEnabled) {
    data = [
      ...data,
      {
        text: 'PEDIA score',
        value: 'pedia_score',
        sortable: true,
      },
    ]
  }
  return data
}

const extraAnnoFieldFormat = (value, pos) => {
  if (!value) return '-'
  const ret = parseFloat(value[0][pos - 1])
  return Number.isInteger(ret) ? ret : formatFloat(ret, 4)
}

const tableHeaders = computed(() => {
  return [
    { text: 'variant icons', value: 'variant_icons', hidden: true },
    ...coordinatesClinvarColumns(),
    { text: 'frequency', value: 'frequency', sortable: true },
    { text: '#hom', value: 'homozygous', sortable: true },
    { text: 'constraint', value: 'constraints', sortable: true },
    { text: 'gene', value: 'gene', sortable: true },
    { text: 'gene icons', value: 'gene_icons', sortable: true },
    ...optionalColumns(),
    ...genotypeColumns(),
    ...scoreColumns(),
    { text: '', value: 'igv' },
  ]
})

/** Rows to display in the table. */
const tableRows = ref([])
/** Whether the Vue3EasyDataTable is loading. */
const tableLoading = ref(false)

const getAcmgRating = (payload) => {
  return acmgRatingStore.getAcmgRating(
    new SeqvarImpl(
      payload.release === 'GRCh37' ? 'grch37' : 'grch38',
      payload.chromosome,
      payload.start,
      payload.reference,
      payload.alternative,
    ),
  )
}

const getFlags = (payload) => {
  return flagsStore.getFlags(
    new SeqvarImpl(
      payload.release === 'GRCh37' ? 'grch37' : 'grch38',
      payload.chromosome,
      payload.start,
      payload.reference,
      payload.alternative,
    ),
  )
}

const hasComments = (payload) => {
  return commentsStore.hasComments(
    new SeqvarImpl(
      payload.release === 'GRCh37' ? 'grch37' : 'grch38',
      payload.chromosome,
      payload.start,
      payload.reference,
      payload.alternative,
    ),
  )
}

const hasProjectComments = (payload) => {
  return commentsStore.hasProjectWideComments(
    new SeqvarImpl(
      payload.release === 'GRCh37' ? 'grch37' : 'grch38',
      payload.chromosome,
      payload.start,
      payload.reference,
      payload.alternative,
    ),
  )
}

const hasProjectFlags = (payload) => {
  return flagsStore.hasProjectWideFlags(
    new SeqvarImpl(
      payload.release === 'GRCh37' ? 'grch37' : 'grch38',
      payload.chromosome,
      payload.start,
      payload.reference,
      payload.alternative,
    ),
  )
}

/**
 * Configuration for the row to color them based on flags.
 */
const tableRowClassName = (item, _rowNumber) => {
  if (item.sodar_uuid === variantResultSetStore.lastVisited) {
    return 'last-visited-row'
  }
  if (!flagsStore.caseFlags) {
    return ''
  }
  const flagColors = ['positive', 'uncertain', 'negative']
  const flags = getFlags(item.payload)
  if (!flags) {
    return ''
  }
  if (flagColors.includes(flags.flag_summary)) {
    return `${flags.flag_summary}-row`
  }
  return flagColors.includes(flags.flag_visual) ||
    flagColors.includes(flags.flag_validation) ||
    flagColors.includes(flags.flag_molecular) ||
    flagColors.includes(flags.flag_phenotype_match) ||
    flags.flag_candidate ||
    flags.flag_doesnt_segregate ||
    flags.flag_final_causative ||
    flags.flag_for_validation ||
    flags.flag_no_disease_association ||
    flags.flag_segregates
    ? 'bookmarked-row'
    : ''
}

const formatFreq = (value) => {
  return formatFloat(value, 5)
}

const formatConstraint = (value) => {
  return formatFloat(value, 3)
}

const getSymbol = (item) => item.symbol || item.gene_symbol || '-'
const getAcmgBadgeClasses = (acmgClass) => {
  const acmgBadgeClasses = ['ml-1', 'badge', getAcmgBadge(acmgClass)]
  if (!acmgClass) {
    acmgBadgeClasses.push('badge-outline')
  }
  return acmgBadgeClasses.join(' ')
}

const freqHomFieldName = computed(() => {
  return displayFrequency.value === DisplayFrequencies.Exac.value
    ? { frequency: 'exac_frequency', homozygous: 'exac_homozygous' }
    : displayFrequency.value === DisplayFrequencies.ThousandGenomes.value
      ? {
          frequency: 'thousand_genomes_frequency',
          homozygous: 'thousand_genomes_homozygous',
        }
      : displayFrequency.value === DisplayFrequencies.GnomadExomes.value
        ? {
            frequency: 'gnomad_exomes_frequency',
            homozygous: 'gnomad_exomes_homozygous',
          }
        : displayFrequency.value === DisplayFrequencies.GnomadGenomes.value
          ? {
              frequency: 'gnomad_genomes_frequency',
              homozygous: 'gnomad_genomes_homozygous',
            }
          : displayFrequency.value === DisplayFrequencies.InhouseDb.value
            ? { frequency: 'inhouse_carriers', homozygous: 'inhouse_hom_alt' }
            : displayFrequency.value === DisplayFrequencies.MtDb.value
              ? { frequency: 'mtdb_frequency', homozygous: 'mtdb_count' }
              : displayFrequency.value === DisplayFrequencies.HelixMtDb.value
                ? {
                    frequency: 'helixmtdb_frequency',
                    homozygous: 'helixmtdb_hom_count',
                  }
                : displayFrequency.value === DisplayFrequencies.Mitomap.value
                  ? {
                      frequency: 'mitomap_frequency',
                      homozygous: 'mitomap_count',
                    }
                  : { frequency: null, homozygous: null }
})

const displayFrequencyContent = (item) => {
  return displayFrequency.value === DisplayFrequencies.InhouseDb.value
    ? item[freqHomFieldName.value.frequency]
    : formatFreq(item[freqHomFieldName.value.frequency])
}

const displayHomozygousContent = (item) => {
  return item[freqHomFieldName.value.homozygous]
}

const constraintFieldName = computed(() => {
  return displayConstraint.value === DisplayConstraints.ExacPli.value
    ? 'exac_pLI'
    : displayConstraint.value === DisplayConstraints.ExacZMis.value
      ? 'exac_mis_z'
      : displayConstraint.value === DisplayConstraints.ExacZSyn.value
        ? 'exac_syn_z'
        : displayConstraint.value === DisplayConstraints.GnomadLoeuf.value
          ? 'gnomad_loeuf'
          : displayConstraint.value === DisplayConstraints.GnomadPli.value
            ? 'gnomad_pLI'
            : displayConstraint.value === DisplayConstraints.GnomadZMis.value
              ? 'gnomad_mis_z'
              : displayConstraint.value === DisplayConstraints.GnomadZSyn.value
                ? 'gnomad_syn_z'
                : null
})

const displayConstraintsContent = (item) => {
  return formatConstraint(item[constraintFieldName.value])
}

const isOnAcmgList = (item) => item.acmg_symbol !== null
const isDiseaseGene = (item) =>
  new String(item.disease_gene).toLowerCase() === 'true'
const sortedModesOfInheritance = (item) => {
  return Array.from(item.modes_of_inheritance).sort()
}
const effectSummary = (item) => {
  return [null, 'p.?', 'p.='].includes(item.hgvs_p) ? item.hgvs_c : item.hgvs_p
}
const goToLocus = async (item) => {
  const chrom = item.chromosome == 'chrMT' ? 'chrM' : item.chromosome
  await fetch(
    `http://127.0.0.1:60151/goto?locus=${chrom}:${item.start}-${item.end}`,
  ).catch(() => {
    const msg =
      "Couldn't connect to IGV. Please make sure IGV is running and try again."
    alert(msg)
    console.error(msg)
  })
}
const mtLink = (item) =>
  item.release === 'GRCh37'
    ? `https://www.genecascade.org/MTc2021/ChrPos102.cgi?chromosome=${item.chromosome}&position=${item.start}&ref=${item.reference}&alt=${item.alternative}`
    : '#'

const getClinvarSignificanceBadge = (patho) => {
  if (patho === 'pathogenic') {
    return 'badge-danger'
  } else if (patho === 'likely pathogenic') {
    return 'badge-warning'
  } else if (patho === 'uncertain significance') {
    return 'badge-info'
  } else if (patho === 'likely benign') {
    return 'badge-secondary'
  } else if (patho === 'benign') {
    return 'badge-secondary'
  }
  return 'badge-secondary'
}

const showVariantDetails = (sodarUuid, section) => {
  variantResultSetStore.lastVisited = sodarUuid
  emit('variantSelected', {
    smallvariantresultrow: sodarUuid,
    selectedSection: section ?? 'gene-overview',
  })
}

const displayAmbiguousFrequencyWarning = (item) => {
  const tables = [
    'exac',
    'thousand_genomes',
    'gnomad_exomes',
    'gnomad_genomes',
    'inhouse',
  ]
  const ambiguousTables = []
  for (const table of tables) {
    const hom_field =
      table === 'inhouse' ? 'inhouse_hom_alt' : table + '_homozygous'
    if (
      item[hom_field] > 50 ||
      (table !== 'inhouse' && item[table + '_frequency'] > 0.1)
    ) {
      ambiguousTables.push(table)
    }
  }
  return ambiguousTables
}

const displayAmbiguousFrequencyWarningBool = ref(false)
const displayGenotypeInconsitencyWarning = () => {
  caseDetailsStore.caseObj?.pedigree.forEach((item) => {
    Object.entries(tableRows.value).forEach(([row_no, row]) => {
      if (!(item.name in row.payload.genotype)) {
        displayAmbiguousFrequencyWarningBool.value = true
        console.warning(
          `Genotype inconsistency: ${item.name} missing in row ${row_no}`,
        )
      } else if (!('gt' in row.payload.genotype[item.name])) {
        displayAmbiguousFrequencyWarningBool.value = true
        console.warning(
          `Genotype inconsistency: ${item.name} genotype has no \`gt\` field in row ${row_no}`,
        )
      }
    })
  })
}

const displayAmbiguousFrequencyWarningMsg = (item) => {
  const tables = displayAmbiguousFrequencyWarning(item)
  const tablesStr = tables.join(' ')
  return `Table(s) ${tablesStr} contain(s) freq > 0.1 or #hom > 50`
}

/** Load data from table as configured by tableServerOptions. */
const loadFromServer = async () => {
  const transmogrify = (row) => {
    row.position =
      (row.chromosome.startsWith('chr')
        ? row.chromosome
        : `chr${row.chromosome}`) +
      ':' +
      formatLargeInt(row.start)
    return row
  }

  const variantClient = new VariantClient(ctxStore.csrfToken)

  tableLoading.value = true
  if (variantResultSetStore.resultSetUuid) {
    const response = await variantClient.listQueryResultRow(
      variantResultSetStore.resultSetUuid,
      {
        pageNo: tableServerOptions.value.page,
        pageSize: tableServerOptions.value.rowsPerPage,
        orderBy:
          tableServerOptions.value.sortBy === 'position'
            ? 'chromosome_no,start'
            : tableServerOptions.value.sortBy === 'gene'
              ? 'symbol'
              : tableServerOptions.value.sortBy === 'gene_icons'
                ? 'acmg_symbol,disease_gene'
                : tableServerOptions.value.sortBy === 'frequency'
                  ? freqHomFieldName.value.frequency
                  : tableServerOptions.value.sortBy === 'homozygous'
                    ? freqHomFieldName.value.homozygous
                    : tableServerOptions.value.sortBy === 'constraints'
                      ? constraintFieldName.value
                      : tableServerOptions.value.sortBy?.startsWith('genotype_')
                        ? caseDetailsStore.genotypeMapping[
                            tableServerOptions.value.sortBy
                          ].sortByName
                        : tableServerOptions.value.sortBy,
        orderDir: tableServerOptions.value.sortType,
      },
    )
    tableRows.value = response.results.map((row) => transmogrify(row))
    tableLoading.value = false
    displayGenotypeInconsitencyWarning()
  }
}

const extraAnnoFields = computed(
  () => variantResultSetStore.extraAnnoFields ?? [],
)

const scrollToLastPosition = () => {
  if (variantQueryStore.lastPosition) {
    const elem = document.querySelector('div#app')
    if (elem) {
      elem.scrollTop = variantQueryStore.lastPosition
    }
  }
}

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

/** Load data when mounted. */
onMounted(async () => {
  if (variantResultSetStore.resultSetUuid) {
    await loadFromServer()
    scrollToLastPosition()
  }
})

watch(
  () => variantResultSetStore.resultSetUuid,
  async (_newValue, _oldValue) => {
    if (_newValue) {
      await loadFromServer()
      scrollToLastPosition()
    }
  },
  { deep: true },
)
</script>

<template>
  <div v-if="displayAmbiguousFrequencyWarningBool" class="alert alert-warning">
    <i-mdi-alert-circle-outline />
    <em class="ml-1"
      ><strong>Data inconsistency warning</strong>: At least one variant is
      missing the genotype information for one or more individuals.</em
    >
  </div>
  <div class="card mb-0 h-100">
    <div class="card-header d-flex flex-row pt-1 pb-1">
      <div class="pr-3 align-self-start record-count">
        <div>
          <label class="font-weight-bold small mb-0 text-nowrap">
            # Records
          </label>
        </div>
        <div class="text-center">
          <span id="results-button" class="btn btn-sm btn-outline-secondary">
            {{ variantResultSetStore?.resultSet?.result_row_count }}
          </span>
        </div>
      </div>
      <ColumnControl
        v-model:display-details="displayDetails"
        v-model:display-frequency="displayFrequency"
        v-model:display-constraint="displayConstraint"
        v-model:display-columns="displayColumns"
        :extra-anno-fields="extraAnnoFields"
      />
      <ExportResults />
    </div>
    <div class="card-body p-0 b-0">
      <EasyDataTable
        v-model:server-options="tableServerOptions"
        table-class-name="customize-table"
        :loading="tableLoading"
        :body-row-class-name="tableRowClassName"
        :server-items-length="
          variantResultSetStore?.resultSet?.result_row_count
        "
        :headers="tableHeaders"
        :items="tableRows"
        :rows-items="[20, 50, 200, 1000]"
        theme-color="#6c757d"
        header-text-direction="left"
        body-text-direction="left"
        show-index
        buttons-pagination
      >
        <template #empty-message>
          <em class="ml-2 text-dark" style="font-size: 150%">
            <strong>No variant passed the current filter settings.</strong
            ><br />
            Please try relaxing your settings.
          </em>
        </template>
        <template #item-variant_icons="{ sodar_uuid, payload }">
          <span class="text-nowrap">
            <i-fa-solid-search
              class="text-muted"
              role="button"
              @click="showVariantDetails(sodar_uuid)"
            />
            <i-fa-solid-bookmark
              v-if="getFlags(payload)"
              :class="`${hasProjectFlags(payload) ? 'text-warning' : 'text-muted'} ml-1`"
              title="flags & bookmarks"
              role="button"
              @click="showVariantDetails(sodar_uuid, 'seqvar-flags')"
            />
            <i-fa-regular-bookmark
              v-else
              :class="`${hasProjectFlags(payload) ? 'text-warning' : 'text-muted'} ml-1`"
              title="flags & bookmarks"
              role="button"
              @click="showVariantDetails(sodar_uuid, 'seqvar-flags')"
            />

            <i-fa-solid-comment
              v-if="hasComments(payload)"
              :class="`${hasProjectComments(payload) ? 'text-warning' : 'text-muted'} ml-1`"
              role="button"
              @click="showVariantDetails(sodar_uuid, 'seqvar-comments')"
            />
            <i-fa-regular-comment
              v-else
              :class="`${hasProjectComments(payload) ? 'text-warning' : 'text-muted'} ml-1`"
              role="button"
              @click="showVariantDetails(sodar_uuid, 'seqvar-comments')"
            />

            <span
              title="ACMG rating"
              :class="getAcmgBadgeClasses(getAcmgRating(payload))"
              role="button"
              @click="showVariantDetails(sodar_uuid, 'seqvar-acmg')"
              >{{ getAcmgRating(payload) || '-' }}</span
            >

            <a
              v-if="payload.rsid"
              target="_blank"
              :href="
                'https://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=' +
                payload.rsid.slice(2)
              "
            >
              <i-fa-solid-database class="ml-1 text-muted" />
            </a>
            <i-fa-solid-database v-else class="ml-1 text-muted icon-inactive" />

            <span
              role="button"
              @click="showVariantDetails(sodar_uuid, 'seqvar-clinvar')"
            >
              <i-fa-regular-hospital
                v-if="payload.in_clinvar && payload.summary_pathogenicity_label"
                class="ml-1 text-muted"
              />
              <i-fa-regular-hospital
                v-else
                title="Not in local ClinVar copy"
                class="ml-1 text-muted icon-inactive"
              />
            </span>
          </span>
        </template>
        <template #item-position="{ sodar_uuid, position }">
          <div
            role="button"
            @click="showVariantDetails(sodar_uuid, 'seqvar-tools')"
          >
            {{ position }}
          </div>
        </template>
        <template #item-reference="{ sodar_uuid, reference }">
          <div
            role="button"
            @click="showVariantDetails(sodar_uuid, 'seqvar-tools')"
          >
            <span :title="reference">{{ truncateText(reference, 5) }}</span>
          </div>
        </template>
        <template #item-alternative="{ sodar_uuid, alternative }">
          <div
            role="button"
            @click="showVariantDetails(sodar_uuid, 'seqvar-tools')"
          >
            <span :title="alternative">{{ truncateText(alternative, 5) }}</span>
          </div>
        </template>
        <template #item-clinvar="{ payload }">
          <span v-if="payload.summary_pathogenicity_label" class="badge-group">
            <span
              class="badge"
              :class="
                getClinvarSignificanceBadge(payload.summary_pathogenicity_label)
              "
            >
              {{ payload.summary_pathogenicity_label }}
            </span>
            <span
              class="badge badge-dark"
              :title="payload.summary_review_status_label"
            >
              <i-fa-solid-star
                v-for="i in payload.summary_gold_stars"
                :key="i"
              />
              <i-fa-regular-star
                v-for="j in 4 - payload.summary_gold_stars"
                :key="j"
              />
            </span>
          </span>
          <span v-else class="badge badge-light">-</span>
        </template>
        <template #item-frequency="{ sodar_uuid, payload }">
          <div
            role="button"
            @click="showVariantDetails(sodar_uuid, 'seqvar-freqs')"
          >
            <abbr
              v-if="displayAmbiguousFrequencyWarning(payload)?.length"
              :title="displayAmbiguousFrequencyWarningMsg(payload)"
            >
              {{ displayFrequencyContent(payload) }}
              <i-mdi-information-outline />
            </abbr>
            <span v-else>
              {{ displayFrequencyContent(payload) }}
            </span>
          </div>
        </template>
        <template #item-homozygous="{ sodar_uuid, payload }">
          <div
            role="button"
            @click.prevent="showVariantDetails(sodar_uuid, 'seqvar-freqs')"
          >
            {{ displayHomozygousContent(payload) }}
          </div>
        </template>
        <template #item-constraints="{ sodar_uuid, payload }">
          <div
            role="button"
            @click.prevent="showVariantDetails(sodar_uuid, 'gene-overview')"
          >
            {{ displayConstraintsContent(payload) }}
          </div>
        </template>
        <template #item-gene="{ sodar_uuid, payload }">
          <span
            class="user-select-none"
            href="#"
            role="button"
            @click.prevent="showVariantDetails(sodar_uuid, 'gene-overview')"
          >
            {{ getSymbol(payload) }}
          </span>
        </template>
        <template #item-gene_icons="{ payload }">
          <span class="text-nowrap">
            <i-fa-solid-user-md
              :class="{
                'text-danger': isOnAcmgList(payload),
                'text-muted icon-inactive': !isOnAcmgList(payload),
              }"
              title="Gene in ACMG incidental finding list"
            />
            <i-fa-solid-lightbulb
              v-if="isDiseaseGene(payload)"
              class="text-danger align-baseline"
              title="Known disease gene"
            />
            <i-fa-regular-lightbulb
              v-if="!isDiseaseGene(payload)"
              class="text-muted icon-inactive align-baseline"
              title="Not a known disease gene"
            />
            <span v-if="payload.modes_of_inheritance">
              <span
                v-for="(mode, index) in sortedModesOfInheritance(payload)"
                :key="index"
                class="badge badge-info ml-1"
                >{{ mode }}</span
              >
            </span>
          </span>
        </template>
        <template #item-effect_summary="{ sodar_uuid, payload }">
          <span
            :title="`${effectSummary(payload)} [${payload.effect.join(', ')}]`"
            role="button"
            @click="showVariantDetails(sodar_uuid, 'seqvar-csq')"
          >
            {{ truncateText(effectSummary(payload), 12) }}
          </span>
        </template>
        <template #item-effect="{ payload }">
          {{ payload.effect.join(', ') }}
        </template>
        <template #item-hgvs_p="{ payload }">
          <span :title="payload.hgvs_p">{{
            truncateText(payload.hgvs_p, 12)
          }}</span>
        </template>
        <template #item-hgvs_c="{ payload }">
          <span :title="payload.hgvs_c">{{
            truncateText(payload.hgvs_c, 12)
          }}</span>
        </template>
        <template #item-exon_dist="{ payload }">
          {{ payload.exon_dist }}
        </template>
        <template
          v-for="{ field } in extraAnnoFields"
          #[`item-extra_anno${field}`]="{ payload }"
        >
          {{ extraAnnoFieldFormat(payload.extra_annos, field) }}
        </template>
        <template
          v-for="{ name } in caseDetailsStore.caseObj?.pedigree"
          #[`item-genotype_${displayName(name)}`]="{ payload }"
        >
          <template v-if="!(name in payload.genotype)">
            <span
              title="Info for the admin: the individual has no genotype information for this variant."
            >
              <i-mdi-do-not-disturb-on />
            </span>
          </template>
          <template v-else-if="!('gt' in payload.genotype[name])">
            <span
              title="Info for the admin: the `gt` field in the genotype information of the individual is missing."
            >
              <i-mdi-do-not-disturb-on />
              <em><sup>gt</sup></em>
            </span>
          </template>
          <template v-else>
            {{ payload.genotype[name].gt }}
          </template>
        </template>
        <template #item-pathogenicity_score="{ payload }">
          {{ formatFloat(payload.pathogenicity_score, 3) }}
        </template>
        <template #item-phenotype_score="{ payload }">
          {{ formatFloat(payload.phenotype_score, 3) }}
        </template>
        <template #item-patho_pheno_score="{ payload }">
          {{ formatFloat(payload.patho_pheno_score, 3) }}
        </template>
        <template #item-gm_score="{ payload }">
          {{ formatFloat(payload.gm_score, 3) }}
        </template>
        <template #item-pedia_score="{ payload }">
          {{ formatFloat(payload.pedia_score, 3) }}
        </template>
        <template #item-igv="item">
          <div class="btn-group btn-group-sm">
            <div
              title="Flags the variant as an artifact by setting visually negative and summary negative flags."
              class="btn btn-sm btn-outline-secondary"
              style="font-size: 80%"
              role="button"
              @click="
                flagsStore.flagAsArtifact(
                  new SeqvarImpl(
                    item.release === 'GRCh37' ? 'grch37' : 'grch38',
                    item.chromosome,
                    item.start,
                    item.reference,
                    item.alternative,
                  ),
                  item.sodar_uuid,
                )
              "
            >
              <i-fa-solid-thumbs-down class="text-muted" />
            </div>
            <a
              :href="mtLink(item)"
              target="_blank"
              style="font-size: 80%"
              class="btn btn-sm btn-outline-secondary"
              :class="mtLink(item) === '#' ? 'disabled' : ''"
            >
              MT
            </a>
            <button
              type="button"
              title="Go to locus in IGV"
              style="font-size: 80%"
              class="btn btn-sm btn-secondary"
              role="button"
              @click="goToLocus(item)"
            >
              IGV
            </button>
          </div>
        </template>
      </EasyDataTable>
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
.icon-inactive {
  opacity: 30%;
}
.badge-outline {
  border: 1px solid #cccccc;
}
.badge-group {
  padding: 2px;
  display: inline-flex;
}

.badge-group > .badge:not(:first-child):not(:last-child) {
  border-radius: 0;
  margin-left: 0;
  margin-right: 0;
}

.badge-group > .badge:first-child {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  margin-right: 0;
}

.badge-group > .badge:last-child {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  margin-left: 0;
}
</style>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
