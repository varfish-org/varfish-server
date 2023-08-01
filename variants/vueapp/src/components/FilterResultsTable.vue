<script setup>
import EasyDataTable from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'
import { computed, onBeforeMount, onMounted, ref, watch } from 'vue'
import {
  displayName,
  formatLargeInt,
  formatFloat,
  truncateText,
} from '@varfish/helpers.js'
import { getAcmgBadge } from '@variants/helpers.js'
import variantsApi from '@variants/api/variants.js'
import ColumnControl from './ColumnControl.vue'
import ExportResults from './ExportResults.vue'
import { useVariantDetailsStore } from '@variants/stores/variantDetails'
import { useVariantFlagsStore } from '@variants/stores/variantFlags'
import { useVariantCommentsStore } from '@variants/stores/variantComments'
import { useFilterQueryStore } from '@variants/stores/filterQuery'
import { useVariantAcmgRatingStore } from '@variants/stores/variantAcmgRating'
import { copy, declareWrapper } from '../helpers'
import {
  DisplayConstraints,
  DisplayConstraintsToText,
  DisplayFrequencies,
  DisplayColumnsToText,
  DisplayDetails,
} from '@variants/enums'

/**
 * The component's props.
 */
const props = defineProps({
  /** The case with the property to display for. */
  case: Object,
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
  /** The pathogenicity score enabled. */
  pathoEnabled: Boolean,
  /** The phenotype score enabled. */
  prioEnabled: Boolean,
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
  emit,
)
/** Wrapper around {@code displayColumns} prop. */
const displayColumnsWrapper = declareWrapper(props, 'displayColumns', emit)
/** The table server options, updated by Vue3EasyDataTable. */
const tableServerOptions = ref({
  page: 1,
  rowsPerPage: 50,
  sortBy: 'position',
  sortType: 'asc',
})

const context = ref(null)

/**
 * Setup stores before mounting the component.
 */
const detailsStore = useVariantDetailsStore()
const queryStore = useFilterQueryStore()
const flagsStore = useVariantFlagsStore()
const commentsStore = useVariantCommentsStore()
const acmgRatingStore = useVariantAcmgRatingStore()

/** Update display when pagination or sorting changed. */
/**
watch(
  [
    () => queryStore.tableServerOptions.page,
    () => queryStore.tableServerOptions.rowsPerPage,
    () => queryStore.tableServerOptions.sortBy,
    () => queryStore.tableServerOptions.sortType,
  ],
  async (
    [_newPageNo, _newRowsPerPage, _newSortBy, _newSortType],
    [_oldPageNo, _oldRowsPerPage, _oldSortBy, _oldSortType]
  ) => {
    queryStore.queryState = QueryStates.Resuming.value
    await queryStore.runFetchLoop(queryStore.previousQueryDetails.sodar_uuid)
  }
)
*/

onBeforeMount(() => {
  tableLoading.value = true
  const appContext = { csrf_token: queryStore.csrfToken }
  Promise.all([
    flagsStore.initialize(appContext, queryStore.caseUuid),
    commentsStore.initialize(appContext, queryStore.caseUuid),
    acmgRatingStore.initialize(appContext, queryStore.caseUuid),
  ]).then(() => {
    tableLoading.value = false
  })
})

// const displayConstraintText = computed(() => {
//   /** TODO Somehow it displays the string with quotes ... :/ */
//   return DisplayConstraintsToText[displayConstraintWrapper.value]
// })

/**
 * Setup for easy-data-table.
 */

const coordinatesClinvarColumns = () => {
  if (props.displayDetails === DisplayDetails.Clinvar.value) {
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
  for (const { field, label } of props.extraAnnoFields) {
    optionalColumnTexts[`extra_anno${field}`] = label
  }
  return props.displayColumns.map((field) => ({
    text: optionalColumnTexts[field],
    value: field,
    sortable: field.startsWith('extra_anno'),
  }))
}

const genotypeMapping = {}
const genotypeColumns = () => {
  if (!props.case) {
    return []
  }
  return props.case.pedigree.map(({ name }) => {
    genotypeMapping[`genotype_${displayName(name)}`] = name
    return {
      text: displayName(name),
      value: `genotype_${displayName(name)}`,
      sortable: true,
    }
  })
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
  return data
}

const extraAnnoFieldFormat = (value, pos) => {
  if (!value) return '-'
  let ret = parseFloat(value[0][pos - 1])
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

/**
 * Configuration for the ag-grid row to color them based on flags.
 */
const tableRowClassName = (item, _rowNumber) => {
  if (!flagsStore.caseFlags) {
    return ''
  }
  const flagColors = ['positive', 'uncertain', 'negative']
  const flags = flagsStore.getFlags(item.payload)
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
  let acmgBadgeClasses = ['ml-1', 'badge', getAcmgBadge(acmgClass)]
  if (!acmgClass) {
    acmgBadgeClasses.push('badge-outline')
  }
  return acmgBadgeClasses.join(' ')
}

const freqHomFieldName = computed(() => {
  return displayFrequencyWrapper.value === DisplayFrequencies.Exac.value
    ? { frequency: 'exac_frequency', homozygous: 'exac_homozygous' }
    : displayFrequencyWrapper.value === DisplayFrequencies.ThousandGenomes.value
    ? {
        frequency: 'thousand_genomes_frequency',
        homozygous: 'thousand_genomes_homozygous',
      }
    : displayFrequencyWrapper.value === DisplayFrequencies.GnomadExomes.value
    ? {
        frequency: 'gnomad_exomes_frequency',
        homozygous: 'gnomad_exomes_homozygous',
      }
    : displayFrequencyWrapper.value === DisplayFrequencies.GnomadGenomes.value
    ? {
        frequency: 'gnomad_genomes_frequency',
        homozygous: 'gnomad_genomes_homozygous',
      }
    : displayFrequencyWrapper.value === DisplayFrequencies.InhouseDb.value
    ? { frequency: 'inhouse_carriers', homozygous: 'inhouse_hom_alt' }
    : displayFrequencyWrapper.value === DisplayFrequencies.MtDb.value
    ? { frequency: 'mtdb_frequency', homozygous: 'mtdb_count' }
    : displayFrequencyWrapper.value === DisplayFrequencies.HelixMtDb.value
    ? { frequency: 'helixmtdb_frequency', homozygous: 'helixmtdb_hom_count' }
    : displayFrequencyWrapper.value === DisplayFrequencies.Mitomap.value
    ? { frequency: 'mitomap_frequency', homozygous: 'mitomap_count' }
    : { frequency: null, homozygous: null }
})

const displayFrequencyContent = (item) => {
  return displayFrequencyWrapper.value === DisplayFrequencies.InhouseDb.value
    ? item[freqHomFieldName.value.frequency]
    : formatFreq(item[freqHomFieldName.value.frequency])
}

const displayHomozygousContent = (item) => {
  return item[freqHomFieldName.value.homozygous]
}

const constraintFieldName = computed(() => {
  return displayConstraintWrapper.value === DisplayConstraints.ExacPli.value
    ? 'exac_pLI'
    : displayConstraintWrapper.value === DisplayConstraints.ExacZMis.value
    ? 'exac_mis_z'
    : displayConstraintWrapper.value === DisplayConstraints.ExacZSyn.value
    ? 'exac_syn_z'
    : displayConstraintWrapper.value === DisplayConstraints.GnomadLoeuf.value
    ? 'gnomad_loeuf'
    : displayConstraintWrapper.value === DisplayConstraints.GnomadPli.value
    ? 'gnomad_pLI'
    : displayConstraintWrapper.value === DisplayConstraints.GnomadZMis.value
    ? 'gnomad_mis_z'
    : displayConstraintWrapper.value === DisplayConstraints.GnomadZSyn.value
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
  const chrPrefixed = item.chromosome.startsWith('chr')
    ? item.chromosome
    : `chr${item.chromosome}`
  await fetch(
    `http://127.0.0.1:60151/goto?locus=${chrPrefixed}:${item.start}-${item.end}`,
  ).catch((e) => {
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
  emit('variantSelected', {
    smallvariantresultrow: sodarUuid,
    selectedTab: section ?? 'gene',
  })
}

const showAcmgRating = (sodarUuid) => {
  emit('variantSelected', {
    smallvariantresultrow: sodarUuid,
    selectedTab: 'acmg-rating',
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
  let ambiguousTables = []
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

  tableLoading.value = true
  const response = await variantsApi.listQueryResultRow(
    queryStore.csrfToken,
    queryStore.queryResultSet.sodar_uuid,
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
          ? 'genotype_' + genotypeMapping[tableServerOptions.value.sortBy]
          : tableServerOptions.value.sortBy,
      orderDir: tableServerOptions.value.sortType,
    },
  )
  tableRows.value = response.results.map((row) => transmogrify(row))
  tableLoading.value = false
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
  { deep: true },
)

watch(
  displayFrequencyWrapper,
  (_newValue, _oldValue) => {
    loadFromServer()
  },
  { deep: true },
)

watch(
  displayConstraintWrapper,
  (_newValue, _oldValue) => {
    loadFromServer()
  },
  { deep: true },
)
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
            {{ queryStore.queryResultSet.result_row_count }}
          </span>
        </div>
      </div>
      <ColumnControl
        :extra-anno-fields="props.extraAnnoFields"
        v-model:display-details="displayDetailsWrapper"
        v-model:display-frequency="displayFrequencyWrapper"
        v-model:display-constraint="displayConstraintWrapper"
        v-model:display-columns="displayColumnsWrapper"
      />
      <ExportResults />
    </div>
    <div class="card-body p-0 b-0">
      <EasyDataTable
        v-model:server-options="tableServerOptions"
        table-class-name="customize-table"
        :loading="tableLoading"
        :body-row-class-name="tableRowClassName"
        :server-items-length="queryStore.queryResultSet.result_row_count"
        :headers="tableHeaders"
        :items="tableRows"
        :rows-items="[20, 50, 200, 1000]"
        theme-color="#6c757d"
        header-text-direction="left"
        body-text-direction="left"
        show-index
        buttons-pagination
      >
        <template #item-variant_icons="{ sodar_uuid, payload }">
          <span class="text-nowrap">
            <i-fa-solid-search
              class="text-muted"
              @click="showVariantDetails(sodar_uuid)"
              role="button"
            />
            <i-fa-solid-bookmark
              v-if="flagsStore.getFlags(payload)"
              class="text-muted ml-1"
              title="flags & bookmarks"
              @click="showVariantDetails(sodar_uuid, 'flags')"
              role="button"
            />
            <i-fa-regular-bookmark
              v-else
              class="text-muted ml-1"
              title="flags & bookmarks"
              @click="showVariantDetails(sodar_uuid, 'flags')"
              role="button"
            />

            <i-fa-solid-comment
              v-if="commentsStore.hasComments(payload)"
              class="text-muted ml-1"
              @click="showVariantDetails(sodar_uuid, 'comments')"
              role="button"
            />
            <i-fa-regular-comment
              v-else
              class="text-muted ml-1"
              @click="showVariantDetails(sodar_uuid, 'comments')"
              role="button"
            />

            <span
              title="ACMG rating"
              :class="
                getAcmgBadgeClasses(acmgRatingStore.getAcmgRating(payload))
              "
              @click="showVariantDetails(sodar_uuid, 'acmg-rating')"
              role="button"
              >{{ acmgRatingStore.getAcmgRating(payload) || '-' }}</span
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
              @click="showVariantDetails(sodar_uuid, 'clinvar')"
              role="button"
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

            <a
              v-if="payload.hgmd_public_overlap"
              target="_blank"
              :href="
                'http://www.hgmd.cf.ac.uk/ac/gene.php?gene=' +
                getSymbol(payload) +
                '&accession=' +
                payload.hgmd_accession
              "
            >
              <i-fa-solid-globe class="ml-1 text-muted" />
            </a>
            <i-fa-solid-globe v-else class="ml-1 text-muted icon-inactive" />
          </span>
        </template>
        <template #item-position="{ sodar_uuid, position }">
          <div
            @click="showVariantDetails(sodar_uuid, 'variant-tools')"
            role="button"
          >
            {{ position }}
          </div>
        </template>
        <template #item-reference="{ sodar_uuid, reference }">
          <div
            @click="showVariantDetails(sodar_uuid, 'variant-tools')"
            role="button"
          >
            <span :title="reference">{{ truncateText(reference, 5) }}</span>
          </div>
        </template>
        <template #item-alternative="{ sodar_uuid, alternative }">
          <div
            @click="showVariantDetails(sodar_uuid, 'variant-tools')"
            role="button"
          >
            <span :title="alternative">{{ truncateText(alternative, 5) }}</span>
          </div>
        </template>
        <template #item-clinvar="{ payload }">
          <span class="badge-group" v-if="payload.summary_pathogenicity_label">
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
          <div @click="showVariantDetails(sodar_uuid, 'freqs')" role="button">
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
          <div @click="showVariantDetails(sodar_uuid, 'freqs')" role="button">
            {{ displayHomozygousContent(payload) }}
          </div>
        </template>
        <template #item-constraints="{ payload }">
          <div
            @click.prevent="showVariantDetails(sodar_uuid, 'gene')"
            role="button"
          >
            {{ displayConstraintsContent(payload) }}
          </div>
        </template>
        <template #item-gene="{ sodar_uuid, payload }">
          <span
            class="user-select-none"
            href="#"
            @click.prevent="showVariantDetails(sodar_uuid, 'gene')"
            role="button"
          >
            {{ getSymbol(payload) }}
          </span>
        </template>
        <template #item-gene_icons="{ payload }">
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
        </template>
        <template #item-effect_summary="{ sodar_uuid, payload }">
          <span
            :title="`${effectSummary(payload)} [${payload.effect.join(', ')}]`"
            @click="showVariantDetails(sodar_uuid, 'tx-csq')"
            role="button"
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
          v-slot:[`item-extra_anno${field}`]="{ payload }"
        >
          {{ extraAnnoFieldFormat(payload.extra_annos, field) }}
        </template>
        <template
          v-for="{ name } in props.case?.pedigree"
          v-slot:[`item-genotype_${displayName(name)}`]="{ payload }"
        >
          {{ payload.genotype[name].gt }}
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
        <template #item-igv="{ payload }">
          <div class="btn-group btn-group-sm">
            <div
              class="btn btn-sm btn-outline-secondary"
              style="font-size: 80%"
              @click="flagsStore.flagAsArtifact(payload)"
              role="button"
            >
              <i-fa-solid-thumbs-down class="text-muted" />
            </div>
            <a
              :href="mtLink(payload)"
              target="_blank"
              style="font-size: 80%"
              class="btn btn-sm btn-outline-secondary"
              :class="mtLink(payload) === '#' ? 'disabled' : ''"
            >
              MT
            </a>
            <button
              @click="goToLocus(payload)"
              type="button"
              title="Go to locus in IGV"
              style="font-size: 80%"
              class="btn btn-sm btn-secondary"
              role="button"
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
