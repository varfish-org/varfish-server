<script setup lang="ts">
import { CaseSerializerNg } from '@varfish-org/varfish-api/lib'
import debounce from 'lodash.debounce'
import { Ref, computed, ref, watch } from 'vue'

import { SortBy } from '@/cases/components/CaseListTable/types'
import CellGeneFlags from '@/seqvars/components/QueryResults/CellGeneFlags.vue'
import ClingenDosage from '@/seqvars/components/QueryResults/ClingenDosage.vue'
import { useResultRowListQuery } from '@/seqvars/queries/seqvarResultRow'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

/**
 * Displays the results table for query results.
 */

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** Teleport target. */
    teleportTo?: HTMLElement
    /** UUID of the case to edit queries for. */
    caseUuid: string
    /** UUID of the case analysis session to edit queries for. */
    sessionUuid: string
    /** UUID of the query. */
    queryUuid: string
    /** UUID of the query execution. */
    queryExecutionUuid: string
    /** UUID of the query result set. */
    resultSetUuid: string
    /** Total row count. */
    totalRowCount: number
    /** The current case. */
    caseObj: CaseSerializerNg
    /** Whether showing hints is enabled. */
    hintsEnabled?: boolean
  }>(),
  {
    hintsEnabled: false,
  },
)

/** This component's events. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits<{
  message: [message: SnackbarMessage]
}>()

interface HeaderDef {
  title: string
  key: string
  width?: number
  sortable?: boolean
}

/** Headers to be used in the `VDataTableServer`. */
const BASE_HEADERS: HeaderDef[] = [
  { title: '#', key: 'index', width: 50, sortable: false },
  { title: 'chrom', key: 'chrom', width: 100, sortable: true },
  { title: 'pos', key: 'pos', width: 50, sortable: true },
  { title: 'ref_allele', key: 'ref_allele', width: 50, sortable: true },
  { title: 'alt_allele', key: 'alt_allele', width: 50, sortable: true },
  {
    title: 'gene symbol',
    key: 'payload.variant_annotation.gene.identity.gene_symbol',
  },
  {
    title: 'HGNC ID',
    key: 'payload.variant_annotation.gene.identity.hgnc_id',
  },
  {
    title: 'hgvs_t',
    key: 'payload.variant_annotation.gene.consequences.hgvs_t',
  },
  {
    title: 'hgvs_p',
    key: 'payload.variant_annotation.gene.consequences.hgvs_p',
  },
  {
    title: 'ClinGen HI',
    key: '__clingen_hi__',
  },
  {
    title: 'ClinGen TS',
    key: '__clingen_ts__',
  },
  {
    title: 'gene flags',
    key: '__gene_flags__',
  },
  {
    title: 'effect',
    key: '__effect__',
  },
  {
    title: 'consequences',
    key: 'payload.variant_annotation.gene.consequences.consequences',
  },
  {
    title: 'pLI gnomAD',
    key: 'payload.variant_annotation.gene.constraints.gnomad.pli',
  },
  {
    title: 'mis-z gnomAD',
    key: 'payload.variant_annotation.gene.constraints.gnomad.mis_z',
  },
  {
    title: 'syn-z gnomAD',
    key: 'payload.variant_annotation.gene.constraints.gnomad.syn_z',
  },
  {
    title: 'o/e lof gnomAD',
    key: 'payload.variant_annotation.gene.constraints.gnomad.oe_lof',
  },
  {
    title: 'o/e mis gnomAD',
    key: 'payload.variant_annotation.gene.constraints.gnomad.oe_mis',
  },
  {
    title: 'o/e lof lower gnomAD',
    key: 'payload.variant_annotation.gene.constraints.gnomad.oe_lof_lower',
  },
  {
    title: 'LOEUF gnomAD',
    key: 'payload.variant_annotation.gene.constraints.gnomad.oe_lof_upper',
  },
  {
    title: 'o/e mis lower gnomAD',
    key: 'payload.variant_annotation.gene.constraints.gnomad.oe_mis_lower',
  },
  {
    title: 'o/e mis upper gnomAD',
    key: 'payload.variant_annotation.gene.constraints.gnomad.oe_mis_upper',
  },
  {
    title: 'HI Percentile',
    key: 'payload.variant_annotation.gene.constraints.decipher.hi_percentile',
  },
  {
    title: 'HI Index',
    key: 'payload.variant_annotation.gene.constraints.decipher.hi_index',
  },
  {
    title: 'RCNV pHaplo',
    key: 'payload.variant_annotation.gene.constraints.rcnv.p_haplo',
  },
  {
    title: 'RCNV pTriplo',
    key: 'payload.variant_annotation.gene.constraints.rcnv.p_triplo',
  },
  {
    title: 'sHet',
    key: 'payload.variant_annotation.gene.constraints.shet.s_het',
  },
  {
    title: 'dbSNP ID',
    key: 'payload.variant_annotation.variant.dbids.dbsnp_id',
  },
  {
    title: '% freq. gnomAD-exomes',
    key: 'payload.variant_annotation.variant.frequency.gnomad_exomes.af',
  },
  {
    title: '# hom.alt. gnomAD-exomes',
    key: 'payload.variant_annotation.variant.frequency.gnomad_exomes.homalt',
  },
  {
    title: '# het. gnomAD-exomes',
    key: 'payload.variant_annotation.variant.frequency.gnomad_exomes.het',
  },
  {
    title: '# hemi.alt. gnomAD-exomes',
    key: 'payload.variant_annotation.variant.frequency.gnomad_exomes.hemialt',
  },
  {
    title: '% freq. gnomAD-genomes',
    key: 'payload.variant_annotation.variant.frequency.gnomad_genomes.af',
  },
  {
    title: '# hom.alt. gnomAD-genomes',
    key: 'payload.variant_annotation.variant.frequency.gnomad_genomes.homalt',
  },
  {
    title: '# het. gnomAD-genomes',
    key: 'payload.variant_annotation.variant.frequency.gnomad_genomes.het',
  },
  {
    title: '# hemi.alt. gnomAD-genomes',
    key: 'payload.variant_annotation.variant.frequency.gnomad_genomes.hemialt',
  },
  {
    title: '% freq. HelixMtDb',
    key: 'payload.variant_annotation.variant.frequency.helixmtdb.af',
  },
  {
    title: '# het. HelixMtDb',
    key: 'payload.variant_annotation.variant.frequency.helixmtdb.het',
  },
  {
    title: '# hom.alt. HelixMtDb',
    key: 'payload.variant_annotation.variant.frequency.helixmtdb.homalt',
  },
  {
    title: '% freq. gnomAD-mtDNA',
    key: 'payload.variant_annotation.variant.frequency.gnomad_mtdna.af',
  },
  {
    title: '# het. gnomAD-mtDNA',
    key: 'payload.variant_annotation.variant.frequency.gnomad_mtdna.het',
  },
  {
    title: '# hom.alt. gnomAD-mtDNA',
    key: 'payload.variant_annotation.variant.frequency.gnomad_mtdna.homalt',
  },
  {
    title: '# het. in-house',
    key: 'payload.variant_annotation.variant.frequency.inhouse.het',
  },
  {
    title: '# hom.alt. in-house',
    key: 'payload.variant_annotation.variant.frequency.inhouse.homalt',
  },
  {
    title: '# hemi.alt. in-house',
    key: 'payload.variant_annotation.variant.frequency.inhouse.hemialt',
  },
  // CLINVAR MISSING CLINVAR MISSING CLINVAR MISSING CLINVAR MISSING
  // CLINVAR MISSING CLINVAR MISSING CLINVAR MISSING CLINVAR MISSING
  // CLINVAR MISSING CLINVAR MISSING CLINVAR MISSING CLINVAR MISSING
  {
    title: 'CADD Phred',
    key: 'payload.variant_annotation.variant.scores.entries.cadd_phred',
  },
]
/** Headers for genotype call-related infos. */
const callHeaders = computed<HeaderDef[]>(() => {
  const result = []
  // in the next line, ignore typescript at all
  // @ts-ignore
  for (const { name } of props.caseObj.pedigree_obj?.individual_set ?? {}) {
    result.push(
      {
        title: `Genotype ${name}`,
        key: `payload.variant_annotation.call.call_infos.${name}.genotype`,
      },
      {
        title: `Total Depth ${name}`,
        key: `payload.variant_annotation.call.call_infos.${name}.dp`,
      },
      {
        title: `Alternate Depth ${name}`,
        key: `payload.variant_annotation.call.call_infos.${name}.ad`,
      },
      {
        title: `Genotype Quality ${name}`,
        key: `payload.variant_annotation.call.call_infos.${name}.gq`,
      },
      {
        title: `Phase Set ${name}`,
        key: `payload.variant_annotation.call.call_infos.${name}.ps`,
      },
    )
  }
  return result
})
/** The headers to display, including from calls. */
const headers = computed<HeaderDef[]>(() => {
  return [...BASE_HEADERS, ...callHeaders.value]
})
/** Current page in `VDataTableServer`; component state. */
const page = ref<number | undefined>(undefined)
/** Items per page in `VDataTableServer`; component state. */
const itemsPerPage = ref<number>(20)
/** Sort by in `VDataTableServer`; component state. */
const sortBy = ref<SortBy[]>([{ key: 'name', order: 'asc' }])
/** Table rows to display in `VDataTableServer` as obtained via TanStack Query. */
const tableRows = computed(() => resultRowListRes.data.value?.results ?? [])

/** Query results for result row query. */
const resultRowListRes = useResultRowListQuery(
  computed(() => ({
    resultSetUuid: props.resultSetUuid,
    page: () => page.value,
    pageSize: itemsPerPage,
    orderBy: () => {
      if (sortBy.value.length === 0) {
        return 'name'
      }
      const column = sortBy.value[0].key
      if (column === 'chrom') {
        return 'chrom_no'
      } else {
        return column
      }
    },
    orderDir: () => (sortBy.value[0]?.order === 'desc' ? 'desc' : 'asc'),
  })),
)

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

// Watch for any error and emit a message on any error.
watch(
  () => resultRowListRes.isError,
  (value: Ref<boolean>) => {
    if (value.value) {
      emit('message', {
        text: `Failed to fetch result rows: ${resultRowListRes.error.value?.message}`,
        color: 'error',
      })
    }
  },
)
</script>

<template>
  <v-data-table-server
    v-model:page="page"
    v-model:items-per-page="itemsPerPage"
    v-model:sort-by="sortBy"
    density="compact"
    :headers="headers"
    :items="tableRows"
    :items-length="totalRowCount"
    :loading="resultRowListRes.isPending.value"
    no-data-text="The result set is empty."
    item-value="name"
    @update:options="updateQueryDebounced"
  >
    <template #[`item.__gene_flags__`]="{ item }">
      <CellGeneFlags :item="item" :hints-enabled="hintsEnabled" />
    </template>

    <template #[`item.__clingen_hi__`]="{ item }">
      <ClingenDosage
        :item="item"
        :hints-enabled="hintsEnabled"
        event="haploinsufficiency"
      />
    </template>
    <template #[`item.__clingen_ts__`]="{ item }">
      <ClingenDosage
        :item="item"
        :hints-enabled="hintsEnabled"
        event="triplosensitivity"
      />
    </template>

    <template #[`item.__effect__`]="{ item }">
      <template
        v-if="
          (item.payload?.variant_annotation?.gene?.consequences?.hgvs_p ??
            'p.?') === 'p.?'
        "
      >
        {{ item.payload?.variant_annotation?.gene?.consequences?.hgvs_t }}
      </template>
      <template v-else>
        {{ item.payload?.variant_annotation?.gene?.consequences?.hgvs_p }}
      </template>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.consequences.consequences`]="{
        item,
      }"
    >
      {{
        item.payload?.variant_annotation?.gene?.consequences?.consequences?.join(
          ', ',
        )
      }}
    </template>

    <template #bottom>
      <Teleport v-if="!!teleportTo" :to="teleportTo">
        <div class="d-flex flex-row align-center">
          <v-select
            v-model="itemsPerPage"
            class="mt-1 mr-3"
            label="page size"
            :items="[10, 20, 50, 100]"
            variant="outlined"
            density="compact"
            hide-details
          />

          <div>
            {{ ((page ?? 1) - 1) * itemsPerPage + 1 }}
            -
            {{ Math.min((page ?? 1) * itemsPerPage, totalRowCount) }}
            of {{ totalRowCount }}
          </div>
          <v-btn
            :disabled="page === 1"
            density="compact"
            icon="$prev"
            variant="outlined"
            rounded="lg"
            class="ml-2 mr-1"
            @click="page = (page ?? 1) - 1"
          />
          <v-btn
            :disabled="page === Math.ceil(totalRowCount / itemsPerPage)"
            density="compact"
            icon="$next"
            variant="outlined"
            rounded="lg"
            @click="page = (page ?? 1) + 1"
          />
        </div>
      </Teleport>
    </template>
  </v-data-table-server>
</template>
