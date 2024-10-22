<script setup lang="ts">
import {
  CaseSerializerNg,
  ClinvarAggregateGermlineReviewStatusChoice,
  SeqvarsVariantConsequenceChoice,
} from '@varfish-org/varfish-api/lib'
import debounce from 'lodash.debounce'
import { sprintf } from 'sprintf-js'
import { Ref, computed, ref, watch } from 'vue'

import { SortBy } from '@/cases/components/CaseListTable/types'
import CellGeneFlags from '@/seqvars/components/QueryResults/CellGeneFlags.vue'
import ClingenDosage from '@/seqvars/components/QueryResults/ClingenDosage.vue'
import { useSeqvarQueryRetrieveQuery } from '@/seqvars/queries/seqvarQuery'
import { useResultRowListQuery } from '@/seqvars/queries/seqvarResultRow'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'
import { formatLargeInt } from '@/varfish/helpers'

import { threeToOneAa } from './lib'

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

/** Labels for consequences */
const CONSEQUENCE_LABEL: Record<SeqvarsVariantConsequenceChoice, string> = {
  transcript_ablation: 'tx ablation',
  exon_loss_variant: 'exon loss',
  splice_acceptor_variant: 'spl acceptor',
  splice_donor_variant: 'spl donor',
  stop_gained: 'stop gained',
  frameshift_variant: 'frameshift',
  stop_lost: 'stop-loss',
  start_lost: 'start-loss',
  transcript_amplification: 'tx amplification',
  feature_elongation: 'tx elongation',
  feature_truncation: 'tx truncation',
  disruptive_inframe_insertion: 'inframe ins',
  disruptive_inframe_deletion: 'inframe del',
  conservative_inframe_insertion: 'inframe ins',
  conservative_inframe_deletion: 'inframe del',
  missense_variant: 'missense',
  splice_donor_5th_base_variant: 'spl donor 5th',
  splice_region_variant: 'spl region',
  splice_donor_region_variant: 'spl region',
  splice_polypyrimidine_tract_variant: 'spl polypyrimidine tract',
  start_retained_variant: 'start retained',
  stop_retained_variant: 'stop retained',
  synonymous_variant: 'synonymous',
  coding_sequence_variant: 'coding seq',
  mature_miRNA_variant: 'mature miRNA',
  '5_prime_UTR_exon_variant': "5' UTR exon",
  '5_prime_UTR_intron_variant': "5' UTR intron",
  '3_prime_UTR_exon_variant': "3' UTR exon",
  '3_prime_UTR_intron_variant': "3' UTR intron",
  non_coding_transcript_exon_variant: 'nc tx exon',
  non_coding_transcript_intron_variant: 'nc tx intron',
  upstream_gene_variant: 'upstream',
  downstream_gene_variant: 'downstream',
  TFBS_ablation: 'TFBS ablation',
  TFBS_amplification: 'TFBS amplification',
  TF_binding_site_variant: 'TF binding site',
  regulatory_region_ablation: 'regulatory region ablation',
  regulatory_region_amplification: 'regulatory region amplification',
  regulatory_region_variant: 'regulatory region variant',
  intergenic_variant: 'intergenic',
  intron_variant: 'intronic',
  gene_variant: 'gene variant',
}

/** Review status labels. */
const REVIEW_STATUS_LABELS: Record<
  ClinvarAggregateGermlineReviewStatusChoice,
  string
> = {
  no_classification_provided: 'No classification provided',
  no_assertion_criteria_provided: 'No assertion criteria provided',
  criteria_provided_single_submitter: 'Criteria provided, single submitter',
  criteria_provided_multiple_submitters_no_conflicts:
    'Criteria provided, multiple submitters, no conflict',
  criteria_provided_conflicting_classifications:
    'Criteria provided, conflicting classifications',
  reviewed_by_expert_panel: 'Reviewed by expert panel',
  practice_guideline: 'Practice guideline',
  no_classifications_from_unflagged_records: 'no classification',
  no_classification_for_the_single_variant: 'no classification',
} as const

/** Review status stars */
const REVIEW_STATUS_STARS: Record<
  ClinvarAggregateGermlineReviewStatusChoice,
  number
> = {
  no_classification_provided: 0,
  no_assertion_criteria_provided: 0,
  criteria_provided_single_submitter: 1,
  criteria_provided_multiple_submitters_no_conflicts: 2,
  criteria_provided_conflicting_classifications: 1,
  reviewed_by_expert_panel: 3,
  practice_guideline: 4,
  no_classifications_from_unflagged_records: 0,
  no_classification_for_the_single_variant: 0,
} as const

/** Query as retrieved via TanStack Query. */
const seqvarQueryRes = useSeqvarQueryRetrieveQuery({
  sessionUuid: props.sessionUuid,
  seqvarQueryUuid: props.queryUuid,
})

/** The headers to display, including from calls. */
const headers = computed<HeaderDef[]>(() => {
  const result = []
  const formatColumns = []

  // Collect `INFO` headers.
  for (const column of seqvarQueryRes.data.value?.columnsconfig
    .column_settings ?? []) {
    if (column.visible) {
      if (column.name.includes('__SAMPLE__')) {
        formatColumns.push(column)
      } else {
        result.push({
          title: column.label,
          key: column.name,
        })
      }
    }
  }

  // Collect `FORMAT` headers.
  interface Individual {
    name: string
  }
  for (const { name } of (props.caseObj.pedigree_obj
    ?.individual_set as unknown as Individual[]) ?? []) {
    for (const column of formatColumns) {
      result.push({
        title: column.label.replace('__SAMPLE__', name),
        key: column.name.replace('__SAMPLE__', name),
      })
    }
  }

  return result
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

const formatFixedFloat = (
  value: number | string | null | undefined,
  options?: { decimal?: number; precision?: number; signed?: boolean },
) => {
  const precision = options?.precision ?? 4
  if (typeof value === 'string') {
    return value
  } else if (value === undefined || value === null) {
    return '-'
  } else if (precision === 0) {
    const result = sprintf(`%${options?.decimal ?? 0}d`, value)
    const decimal = options?.decimal ?? 1
    if (result.length < decimal) {
      return ' '.repeat(decimal - result.length) + result
    } else {
      return result
    }
  } else {
    const sign = value < 0 ? -1 : 1
    const absValue = Math.abs(value)
    let rawResult = sprintf(`%.${precision}f`, absValue)
    if (rawResult === sprintf(`%.${precision}f`, 0)) {
      rawResult = `0.${' '.repeat(precision)}`
    }
    const decimalInStr = absValue.toString().split('.')[0].length
    const decimalPadding =
      options?.decimal === undefined
        ? ''
        : ' '.repeat(options?.decimal - decimalInStr)

    return (
      (sign === -1 ? '-' : options?.signed ? ' ' : '') +
      decimalPadding +
      rawResult
    )
  }
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
    <template #[`item.__chrom_pos__`]="{ item }">
      <span class="font-monospaced">
        <template v-if="item.chrom.length == 1">&nbsp;</template>
        {{ item.chrom }}:{{ formatLargeInt(item.pos) }}
      </span>
    </template>

    <template #[`item.ref_allele`]="{ item }">
      <div class="mono-overfloat-4" :title="item.ref_allele">
        {{ item.ref_allele }}
      </div>
    </template>

    <template #[`item.alt_allele`]="{ item }">
      <div class="mono-overfloat-4" :title="item.alt_allele">
        {{ item.alt_allele }}
      </div>
    </template>

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

    <template
      #[`item.payload.variant_annotation.gene.consequences.hgvs_t`]="{ item }"
    >
      <div
        v-if="
          item.payload?.variant_annotation?.gene?.consequences?.hgvs_t?.length
        "
        class="hide-overfloat-120"
        :title="item.payload?.variant_annotation?.gene?.consequences?.hgvs_t"
      >
        {{ item.payload?.variant_annotation?.gene?.consequences?.hgvs_t }}
      </div>
      <div v-else>-</div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.consequences.hgvs_p`]="{ item }"
    >
      <div
        v-if="
          item.payload?.variant_annotation?.gene?.consequences?.hgvs_p?.length
        "
        class="hide-overfloat-120"
        :title="item.payload?.variant_annotation?.gene?.consequences?.hgvs_p"
      >
        {{
          threeToOneAa(
            item.payload?.variant_annotation?.gene?.consequences?.hgvs_p,
          )
        }}
      </div>
      <div v-else>-</div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.consequences.consequences`]="{
        item,
      }"
    >
      <div
        v-if="
          item.payload?.variant_annotation?.gene?.consequences?.consequences
            ?.length
        "
        class="hide-overfloat-120"
        :title="
          item.payload?.variant_annotation?.gene?.consequences?.consequences
            ?.map((csq) => CONSEQUENCE_LABEL[csq])
            .join(', ')
        "
      >
        {{
          item.payload?.variant_annotation?.gene?.consequences?.consequences
            ?.map((csq) => CONSEQUENCE_LABEL[csq])
            .join(', ')
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.gnomad.pli`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.gnomad?.pli,
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.gnomad.mis_z`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.gnomad?.mis_z,
            { precision: 2, signed: true },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.gnomad.syn_z`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.gnomad?.syn_z,
            { precision: 2, signed: true },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.gnomad.oe_lof`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.gnomad?.oe_lof,
            { precision: 2 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.gnomad.oe_mis`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.gnomad?.oe_mis,
            { precision: 2 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.gnomad.oe_lof_lower`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.gnomad
              ?.oe_lof_lower,
            { precision: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.gnomad.oe_lof_upper`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.gnomad
              ?.oe_lof_upper,
            { precision: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.gnomad.oe_mis_lower`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.gnomad
              ?.oe_mis_lower,
            { precision: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.gnomad.oe_mis_upper`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.gnomad
              ?.oe_mis_upper,
            { precision: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.decipher.hi_percentile`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.decipher
              ?.hi_percentile,
            { precision: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.decipher.hi_index`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.decipher
              ?.hi_index,
            { decimal: 2, precision: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.rcnv.p_haplo`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.rcnv?.p_haplo,
            { precision: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.rcnv.p_triplo`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.rcnv?.p_triplo,
            { precision: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.gene.constraints.shet.s_het`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.gene?.constraints?.shet?.s_het,
            { precision: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.gnomad_exomes.af`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            (item.payload?.variant_annotation?.variant?.frequency?.gnomad_exomes
              ?.af ?? 0) * 100.0,
            { decimal: 2, precision: 2 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.gnomad_exomes.homalt`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.gnomad_exomes
              ?.homalt ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.gnomad_exomes.het`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.gnomad_exomes
              ?.het ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.gnomad_exomes.hemialt`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.gnomad_exomes
              ?.hemialt ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.gnomad_genomes.af`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            (item.payload?.variant_annotation?.variant?.frequency
              ?.gnomad_genomes?.af ?? 0) * 100.0,
            { decimal: 2, precision: 2 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.gnomad_genomes.homalt`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.gnomad_genomes
              ?.homalt ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.gnomad_genomes.het`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.gnomad_genomes
              ?.het ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.gnomad_genomes.hemialt`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.gnomad_genomes
              ?.hemialt ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.helixmtdb.af`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            (item.payload?.variant_annotation?.variant?.frequency?.helixmtdb
              ?.af ?? 0) * 100.0,
            { decimal: 2, precision: 2 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.helixmtdb.homalt`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.helixmtdb
              ?.homalt ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.helixmtdb.het`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.helixmtdb
              ?.het ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.gnomad_mtdna.af`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            (item.payload?.variant_annotation?.variant?.frequency?.gnomad_mtdna
              ?.af ?? 0) * 100.0,
            { decimal: 2, precision: 2 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.gnomad_mtdna.homalt`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.gnomad_mtdna
              ?.homalt ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.gnomad_mtdna.het`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.gnomad_mtdna
              ?.het ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.inhouse.het`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.inhouse
              ?.het ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.inhouse.homalt`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.inhouse
              ?.homalt ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.frequency.inhouse.hemialt`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.frequency?.inhouse
              ?.hemialt ?? 0,
            { precision: 0, decimal: 4 },
          )
        }}
      </div>
    </template>

    <!--
    Display number of stars from item.payload.variant_annotation.variant.clinvar.germline_review_status
    according to REVIEW_STATUS_STARS, displaying label via REVIEW_STATUS_LABELS as title.
     -->
    <template
      #[`item.payload.variant_annotation.variant.clinvar.germline_review_status`]="{
        item,
      }"
    >
      <div class="mono" style="white-space: pre">
        <template
          v-if="
            item.payload?.variant_annotation?.variant?.clinvar
              ?.germline_review_status?.length
          "
        >
          <v-rating
            density="compact"
            :length="4"
            :size="18"
            :model-value="
              REVIEW_STATUS_STARS[
                item.payload?.variant_annotation?.variant?.clinvar
                  ?.germline_review_status
              ]
            "
            readonly
          />
          {{
            REVIEW_STATUS_LABELS[
              item.payload?.variant_annotation?.variant?.clinvar
                ?.germline_review_status
            ]
          }}
        </template>
        <template v-else> - </template>
      </div>
    </template>

    <template
      #[`item.payload.variant_annotation.variant.scores.entries.sift`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.scores?.entries?.sift,
            { precision: 2, decimal: 3 },
          )
        }}
      </div>
    </template>
    <template
      #[`item.payload.variant_annotation.variant.scores.entries.polyphen`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.scores?.entries
              ?.polyphen,
            { precision: 2, decimal: 3 },
          )
        }}
      </div>
    </template>
    <template
      #[`item.payload.variant_annotation.variant.scores.entries.cadd_phred`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.scores?.entries
              ?.cadd_phred,
            { precision: 2, decimal: 3 },
          )
        }}
      </div>
    </template>
    <template
      #[`item.payload.variant_annotation.variant.scores.entries.spliceai`]="{
        item,
      }"
    >
      <div class="mono-width-5 text-right" style="white-space: pre">
        {{
          formatFixedFloat(
            item.payload?.variant_annotation?.variant?.scores?.entries
              ?.spliceai,
            { precision: 3, decimal: 1 },
          )
        }}
      </div>
    </template>
    <template
      #[`item.payload.variant_annotation.variant.scores.entries.spliceai_argmax`]="{
        item,
      }"
    >
      <template
        v-if="
          `${item.payload?.variant_annotation?.variant?.scores?.entries?.spliceai_argmax ?? ''}` !=
          ''
        "
      >
        <div class="mono-width-9 text-right" style="white-space: pre">
          {{
            `${item.payload?.variant_annotation?.variant?.scores?.entries?.spliceai_argmax}`.replace(
              'SpliceAI-',
              '',
            )
          }}
        </div>
      </template>
      <template v-else>
        <div class="mono-width-10 text-right" style="white-space: pre">-</div>
      </template>
    </template>

    <template #[`item.__effect__`]="{ item }">
      <template
        v-if="
          (item.payload?.variant_annotation?.gene?.consequences?.hgvs_p ??
            'p.?') === 'p.?'
        "
      >
        <div
          v-if="
            item.payload?.variant_annotation?.gene?.consequences?.hgvs_t?.length
          "
          class="hide-overfloat-100"
          :title="item.payload?.variant_annotation?.gene?.consequences?.hgvs_t"
        >
          {{ item.payload?.variant_annotation?.gene?.consequences?.hgvs_t }}
        </div>
        <div v-else>-</div>
      </template>
      <div
        v-else-if="
          item.payload?.variant_annotation?.gene?.consequences?.hgvs_p?.length
        "
        class="hide-overfloat-100"
        :title="
          threeToOneAa(
            item.payload?.variant_annotation?.gene?.consequences?.hgvs_p,
          )
        "
      >
        {{
          threeToOneAa(
            item.payload?.variant_annotation?.gene?.consequences?.hgvs_p,
          )
        }}
      </div>
      <div v-else>-</div>
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

<style scoped lang="scss">
// Monospaced font.
.font-monospaced {
  font-family: 'Roboto Mono', monospace;
}

// Mixin for <div> with Monospaced font that has a width set but does not overflow.
@mixin mono-width($width: 10ch) {
  font-family: 'Roboto Mono', monospace;
  width: $width;
  white-space: nowrap;
}

// <div>s with monospaced font and different widths.
div.mono-width-5 {
  @include mono-width(5ch);
}
div.mono-width-8 {
  @include mono-width(8ch);
}
div.mono-width-9 {
  @include mono-width(9ch);
}
div.mono-width-10 {
  @include mono-width(10ch);
}

// Mixin for <div> with Monospaced font that can overflow when width is set.
@mixin mono-overfloat($width: 10ch) {
  @include mono-width($width);
  overflow: hidden;
  text-overflow: ellipsis;
}

// <div>s with monospaced font and different widths.
div.mono-overfloat-1 {
  @include mono-overfloat(1ch);
}
div.mono-overfloat-2 {
  @include mono-overfloat(2ch);
}
div.mono-overfloat-3 {
  @include mono-overfloat(3ch);
}
div.mono-overfloat-4 {
  @include mono-overfloat(4ch);
}
div.mono-overfloat-5 {
  @include mono-overfloat(5ch);
}

// Mixin for <div> that can overflow when width is set.
@mixin hide-overfloat($width: 100px) {
  width: $width;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

// <div>s with different widths.
div.hide-overfloat-20 {
  @include hide-overfloat(20px);
}
div.hide-overfloat-50 {
  @include hide-overfloat(50px);
}
div.hide-overfloat-100 {
  @include hide-overfloat(100px);
}
div.hide-overfloat-120 {
  @include hide-overfloat(120px);
}
div.hide-overfloat-150 {
  @include hide-overfloat(150px);
}
</style>
