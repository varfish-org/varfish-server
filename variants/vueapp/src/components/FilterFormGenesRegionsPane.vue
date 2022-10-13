<script setup>
/**
 * Definition of the filter form tab for genes and regions.
 */

import { nextTick, onMounted, ref } from 'vue'

import TokenizingTextarea from './TokenizingTextarea.vue'

const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  /** The query settings to operate on. */
  querySettings: Object,
  /** CSRF token for querying the API. */
  csrfToken: String,
  /** API endpoint for querying genes. */
  lookupGeneApiEndpoint: {
    type: String,
    default: '/geneinfo/api/lookup-gene/',
  },
})

const emit = defineEmits(['update:querySettings'])

const listType = ref('genomic_region')

// tokens copied here once it validates
const genomicRegionArrRef = ref([])
// this is where the text area writes to
const genomicRegionStrRef = ref('')

/** Regular expression for validating a genomic region. */
const regexRegion = new RegExp(
  '^' + // start
    '(?<chrom>(chr)?' + // open chrom
    '(1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|X|Y|M|MT)' + // chrom name
    ')' + // close chrom
    '(:(?<start>(\\d+(,\\d+)*))-(?<stop>(\\d+(,\\d+)*)))?' + // optional range
    '$' // end
)

/** Validation function for genomic region. */
const validateRegion = (token) => {
  const matches = token.match(regexRegion)
  if (
    matches &&
    matches.groups &&
    matches.groups.start &&
    matches.groups.stop
  ) {
    const start = parseInt(matches.groups.start.replace(',', ''))
    const stop = parseInt(matches.groups.stop.replace(',', ''))
    return new Promise((resolved) => {
      resolved({ valid: stop >= start, label: 'example label' })
    })
  } else {
    return new Promise((resolved) => {
      resolved(!!matches)
    })
  }
}

/** Validation function for genes. */
const validateGene = async (token) => {
  const response = await fetch(
    `${props.lookupGeneApiEndpoint}?query=${token}`,
    {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': props.csrfToken,
    }
  )
  if (response.status === 404) {
    return false // not found
  } else {
    // Conversion to JSON will fail with an exception on error.
    const geneInfo = await response.json()
    return !!geneInfo.hgnc_id
  }
}

/** Returns "*" if there is a failure with the given field. */
const indicateFailure = (key) => {
  const theRef = {
    genomic_region: genomicRegionTextareaRef,
    gene_blocklist: geneBlockListRegionTextareaRef,
    gene_allowlist: geneAllowListRegionTextareaRef,
  }[key]
  if (theRef.value && !theRef.value.isValidating() && !theRef.value.isValid()) {
    return '*'
  } else {
    return ''
  }
}

/** Reference to gene allow list TokenizingTextarea */
const geneAllowListRegionTextareaRef = ref(null)
/** Reference to gene block list TokenizingTextarea */
const geneBlockListRegionTextareaRef = ref(null)
/** Reference to genomic regions TokenizingTextarea */
const genomicRegionTextareaRef = ref(null)

/** Return array of invalid text areas. */
const invalidTextareas = () => {
  const result = []
  if (
    geneAllowListRegionTextareaRef.value &&
    !geneAllowListRegionTextareaRef.value.isValid()
  ) {
    result.push('gene allow list')
  }
  if (
    geneBlockListRegionTextareaRef.value &&
    !geneBlockListRegionTextareaRef.value.isValid()
  ) {
    result.push('gene block list')
  }
  if (
    genomicRegionTextareaRef.value &&
    !genomicRegionTextareaRef.value.isValid()
  ) {
    result.push('genomic regions')
  }
  return result
}

/** Whether the tab is valid. */
const isValid = () => {
  return invalidTextareas().length == 0
}

/** Whether any subcomponent on tab is still validating. */
const isValidating = () => {
  return (
    (genomicRegionTextareaRef.value &&
      genomicRegionTextareaRef.value.isValidating()) ||
    (geneBlockListRegionTextareaRef.value &&
      geneBlockListRegionTextareaRef.value.isValidating()) ||
    (geneAllowListRegionTextareaRef.value &&
      geneAllowListRegionTextareaRef.value.isValidating())
  )
}

/** Take values from outside on mounted. */
onMounted(() => {
  genomicRegionArrRef.value = props.querySettings.genomic_region
  genomicRegionStrRef.value = genomicRegionArrRef.value.join(' ')
})

/** Define the exposed functions. */
defineExpose({
  isValid,
  isValidating,
})
</script>

<template>
  <div class="row">
    <div class="col-12">
      <div
        v-if="props.showFiltrationInlineHelp"
        class="alert alert-secondary small p-2 mt-3"
      >
        <i-mdi-information />
        You can use this tab to either a gene allow or block list or to define a
        list of genomic regions.
      </div>

      <div class="form-inline pl-0 pr-0 pb-3 mt-3">
        <label class="mr-2" for="gene-regions-list-type">List Type</label>
        <select
          v-model="listType"
          :class="{ 'is-invalid': !isValid() }"
          class="custom-select"
          id="gene-regions-list-type"
        >
          <option value="gene_allowlist">
            Gene Allow List{{ indicateFailure('gene_allowlist') }}
          </option>
          <option value="gene_blocklist">
            Gene Block List{{ indicateFailure('gene_blocklist') }}
          </option>
          <option value="genomic_region">
            Genomic Regions{{ indicateFailure('genomic_region') }}
          </option>
        </select>
        <div class="invalid-feedback">
          There is a problem with: {{ invalidTextareas().join(', ') }}.
        </div>
      </div>

      <div
        :class="{ 'd-none': listType !== 'genomic_region' }"
        class="form-group"
      >
        <TokenizingTextarea
          ref="genomicRegionTextareaRef"
          v-model="props.querySettings.genomic_region"
          :validate="validateRegion"
        />
        <small class="form-text">
          Enter a list of genomic regions to restrict your query to. For
          example: <code>X</code>, <code>chrX</code>,
          <code>chrX:1,000,000-2,000,000.</code>.
        </small>
      </div>

      <div
        :class="{ 'd-none': listType !== 'gene_allowlist' }"
        class="form-group"
      >
        <TokenizingTextarea
          ref="geneAllowListRegionTextareaRef"
          v-model="props.querySettings.gene_allowlist"
          :validate="validateGene"
        />
        <small class="form-text">
          Enter a list of genes to restrict your query to, separated with
          spaces. You can use gene symbols, HGNC ids, ENSEMBL gene IDs, or
          Entrez Gene IDs. For example, all of the following code for TGDS
          (TDP-glucose 4,6-dehydratase): <code>TGDS</code>,
          <code>HGNC:20324</code>, <code>ENSG00000088451</code>,
          <code>23483</code>.
        </small>
      </div>

      <div
        :class="{ 'd-none': listType !== 'gene_blocklist' }"
        class="form-group"
      >
        <TokenizingTextarea
          ref="geneBlockListRegionTextareaRef"
          v-model="props.querySettings.gene_blocklist"
          :validate="validateGene"
        />
        <small class="form-text">
          Enter a list of genes to
          <strong class="text-dark"> exclude from your query results </strong>,
          separated with spaces. You can use gene symbols, HGNC ids, ENSEMBL
          gene IDs, or Entrez Gene IDs. For example, all of the following code
          for TGDS (TDP-glucose 4,6-dehydratase): <code>TGDS</code>,
          <code>HGNC:20324</code>, <code>ENSG00000088451</code>,
          <code>23483</code>.
        </small>
      </div>
    </div>
  </div>
  <div v-if="filtrationComplexityMode == 'dev'" class="card-footer">
    <i-mdi-account-hard-hat />
    <strong class="pl-2">Developer Info:</strong>
    <code>
      genomic_region = {{ JSON.stringify(querySettings.genomic_region) }},
      gene_allowlist = {{ JSON.stringify(querySettings.gene_allowlist) }},
      gene_blocklist = {{ JSON.stringify(querySettings.gene_blocklist) }}
    </code>
  </div>
</template>

<style></style>
