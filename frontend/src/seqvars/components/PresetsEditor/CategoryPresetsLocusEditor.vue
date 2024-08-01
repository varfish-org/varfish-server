<script setup lang="ts">
import { SeqvarsQueryPresetsLocus } from '@varfish-org/varfish-api/lib'
import { genomeRegionToString, GenomeRegion, parseGenomeRegion } from './lib'
import { ref, onMounted, watch, computed } from 'vue'
import { debounce } from 'lodash'
import { CATEGORY_PRESETS_DEBOUNCE_WAIT } from './lib'
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'
import { VForm } from 'vuetify/lib/components/index.mjs'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { useCtxStore } from '@/varfish/stores/ctx'
import { AnnonarsApiClient, GeneNames } from '@/varfish/api/annonars'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** UUID of the current preset set version. */
    presetSetVersion?: string
    /** UUID of the query presets locus */
    locusPresets?: string
    /** Whether the editor is readonly. */
    readonly: boolean
  }>(),
  { readonly: false },
)

/** This component's events. */
const emit = defineEmits<{
  /** Emit event to show a message. */
  message: [message: SnackbarMessage]
}>()

/** Store with application context, such as CSRF token. */
const ctxStore = useCtxStore()
/** Store with the presets. */
const seqvarsPresetsStore = useSeqvarsPresetsStore()

/** The data that is to be edited by this component; component state. */
const data = ref<SeqvarsQueryPresetsLocus | undefined>(undefined)

/** Shortcut to the number of locus presets, used for rank. */
const maxRank = computed<number>(() => {
  if (props.presetSetVersion === undefined) {
    return 0
  }
  const presetSetVersion = seqvarsPresetsStore.presetSetVersions.get(
    props.presetSetVersion,
  )
  if (!presetSetVersion) {
    return 0
  }
  return presetSetVersion.seqvarsquerypresetslocus_set.length
})

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Genes text area; component state. */
const genesText = ref<string>('')
/** Error message(s) for genes; component state. */
const genesErrors = ref<string>('')
/** Hint(s) for genes; component state. */
const genesHint = ref<string>('')
/** Genome regions text area; component state. */
const genomeRegionsText = ref<string>('')
/** Error message(s) for genome regions; component state. */
const genomeRegionsErrors = ref<string>('')
/** Hint(s) for genome regions; component state. */
const genomeRegionsHint = ref<string>('')
/** Whether to show editor for genes or loci; component state. */
const editorToShow = ref<'genes' | 'loci'>(
  (data.value?.genes?.length ?? 0) > 0 ? 'genes' : 'loci',
)

/** Handler for parsing genes on clicking the button; using the annonars API. */
const parseGenes = async () => {
  // Annonars client to use.
  const annonarsClient = new AnnonarsApiClient(ctxStore.csrfToken)

  // Clear any error message and hints.
  genesErrors.value = ''
  genesHint.value = ''

  // Guard against empty data or genome regions.
  if (data?.value?.genes?.length === undefined) {
    genesErrors.value = 'Invalid data state (should never happen)'
    return
  }
  // Get gene strings from text area.
  const genesArr = genesText.value.split(/[;\s+]/).filter((r) => r.length > 0)

  // Lookup genes with annonars, add to data and/or generate error message.
  const foundGenes = await annonarsClient.lookupGenes(genesArr)

  // Helper function that registers a `GeneNames` with a set of identifiers.
  const registerIdentifier = (geneNames: GeneNames, seenSet: Set<string>) => {
    seenSet.add(geneNames.hgnc_id)
    seenSet.add(geneNames.symbol)
    if (geneNames.ensembl_gene_id) {
      seenSet.add(geneNames.ensembl_gene_id)
    }
    if (geneNames.ncbi_gene_id) {
      seenSet.add(`${geneNames.ncbi_gene_id}`)
    }
  }

  // Collect list of seen identifiers.
  const seen = new Set<string>()
  for (const gene of foundGenes) {
    registerIdentifier(gene, seen)
  }

  // Copy-convert the found genes over to the data, removing duplicates.
  const alreadyAdded = new Set<string>()
  for (const gene of foundGenes) {
    if (
      alreadyAdded.has(gene.hgnc_id) ||
      alreadyAdded.has(gene.symbol) ||
      (gene.ensembl_gene_id && alreadyAdded.has(gene.ensembl_gene_id)) ||
      (gene.ncbi_gene_id && alreadyAdded.has(gene.ncbi_gene_id))
    ) {
      genesHint.value = 'Skipped already present genes.'
      continue
    }
    registerIdentifier(gene, alreadyAdded)

    data.value.genes.push({
      hgnc_id: gene.hgnc_id,
      symbol: gene.symbol,
      name: gene.name,
      ensembl_id: gene.ensembl_gene_id ?? undefined,
      entrez_id: gene.ncbi_gene_id ? parseInt(gene.ncbi_gene_id) : undefined,
    })
  }

  // Helpfully, sort genes by symbol.
  data.value.genes.sort((a, b) => a.symbol.localeCompare(b.symbol))

  // Copy the genes that were not found over back to the text area.
  const invalidGenes: string[] = []
  for (const gene of genesArr) {
    if (!seen.has(gene)) {
      invalidGenes.push(gene)
    }
  }
  if (invalidGenes.length > 0) {
    genesErrors.value = 'Some genome regions could not be parsed.'
  }
  genesText.value = invalidGenes.join(' ')
}

/** Handler for removing genes from data on clicking "close" in chip. */
const removeGene = async (index: number) => {
  // Guard against empty data or genome regions.
  if (!data?.value?.genes?.length) {
    return
  }
  // Remove genome region from data by index.
  data.value.genes.splice(index, 1)
}

/** Handler for parsing genomic regions on clicking the button. */
const parseGenomeRegions = async () => {
  // Clear any error message and hints.
  genomeRegionsErrors.value = ''
  genomeRegionsHint.value = ''

  // Guard against empty data or genome regions.
  if (data?.value?.genome_regions?.length === undefined) {
    genomeRegionsErrors.value = 'Invalid data state (should never happen)'
    return
  }
  // Get genome regions string from text area.
  const genomeRegionsArr = genomeRegionsText.value
    .split(/[;\s+]/)
    .filter((r) => r.length > 0)
  // Loop over genome regions, parse it, add to data and/or generate error message.
  const invalidGenomeRegions: string[] = []
  for (const genomeRegion of genomeRegionsArr) {
    try {
      const parsed = parseGenomeRegion(genomeRegion)
      // Only add to data if not already present; this also ensures that
      // the text description is unique and can be used as `:key` below.
      if (
        !data.value.genome_regions.find(
          (r: GenomeRegion) =>
            genomeRegionToString(r) === genomeRegionToString(parsed),
        )
      ) {
        data.value.genome_regions.push(parsed)
      } else {
        genomeRegionsHint.value = 'Skipped already present genome regions.'
      }
    } catch (e) {
      invalidGenomeRegions.push(genomeRegion)
    }
  }
  if (invalidGenomeRegions.length > 0) {
    genomeRegionsErrors.value = 'Some genome regions could not be parsed.'
  }
  genomeRegionsText.value = invalidGenomeRegions.join(' ')
}

/** Handler for removing genome region from data on clicking "close" in chip. */
const removeGenomeRegion = async (index: number) => {
  // Guard against empty data or genome regions.
  if (!data?.value?.genome_regions?.length) {
    return
  }
  // Remove genome region from data by index.
  data.value.genome_regions.splice(index, 1)
}

/** Fill the data from the store. */
const fillData = () => {
  // Guard against missing preset set version or locus.
  if (
    props.presetSetVersion === undefined ||
    props.locusPresets === undefined
  ) {
    return
  }
  // Attempt to obtain the model from the store.
  const presetSetVersion = seqvarsPresetsStore.presetSetVersions.get(
    props.presetSetVersion,
  )
  if (!presetSetVersion) {
    emit('message', {
      text: 'Failed to find preset set version.',
      color: 'error',
    })
    return
  }
  const locusPresets = presetSetVersion?.seqvarsquerypresetslocus_set.find(
    (elem) => elem.sodar_uuid === props.locusPresets,
  )
  if (!locusPresets) {
    emit('message', {
      text: 'Failed to find locus presets.',
      color: 'error',
    })
    return
  }

  data.value = { ...locusPresets }
}

/**
 * Update the locus presets in the store.
 *
 * Used directly when changing the rank (to minimize UI delay).
 *
 * @param rankDelta The delta to apply to the rank, if any.
 */
const updateLocusPresets = async (rankDelta: number = 0) => {
  console.log('update locus presets')

  // Guard against missing/readonly/non-draft preset set version or missing locus.
  if (
    props.locusPresets === undefined ||
    props.presetSetVersion === undefined ||
    seqvarsPresetsStore.factoryDefaultPresetSetUuids.includes(
      props.locusPresets,
    ) ||
    seqvarsPresetsStore.presetSetVersions.get(props.presetSetVersion)
      ?.status !== PresetSetVersionState.DRAFT ||
    data.value === undefined
  ) {
    return
  }

  // If necessary, update the rank of the other item as well via API and set
  // the new rank to `data.value.rank`.
  if (rankDelta !== 0) {
    const version = seqvarsPresetsStore.presetSetVersions.get(
      props.presetSetVersion,
    )
    if (
      version === undefined ||
      data.value.rank === undefined ||
      data.value.rank + rankDelta < 1 ||
      data.value.rank + rankDelta > maxRank.value
    ) {
      // Guard against invalid rank and version.
      return
    }
    // Find the next smaller or larger item, sort by rank.
    const others = version.seqvarsquerypresetslocus_set.filter((elem) => {
      if (elem.sodar_uuid === props.locusPresets) {
        return false
      }
      if (rankDelta < 0) {
        return (elem.rank ?? 0) < (data.value?.rank ?? 0)
      } else {
        return (elem.rank ?? 0) > (data.value?.rank ?? 0)
      }
    })
    others.sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
    // Then, pick the other item to flip ranks with.
    const other = others[rankDelta < 0 ? others.length - 1 : 0]
    // Store the other's rank in `data.value.rank` and update other via API.
    if (other) {
      const dataRank = data.value.rank
      data.value.rank = other.rank
      other.rank = dataRank
      try {
        await seqvarsPresetsStore.updateQueryPresetsLocus(
          props.presetSetVersion,
          other,
        )
      } catch (error) {
        emit('message', {
          text: 'Failed to update locus presets rank.',
          color: 'error',
        })
      }
    }
  }

  // Guard against invalid form data.
  const validateResult = await formRef.value?.validate()
  if (validateResult?.valid !== true) {
    return
  }
  try {
    await seqvarsPresetsStore.updateQueryPresetsLocus(
      props.presetSetVersion,
      data.value,
    )
  } catch (error) {
    emit('message', {
      text: 'Failed to update locus presets.',
      color: 'error',
    })
  }
}

/**
 * Update the locus presets in the store -- debounced.
 *
 * Used for updating non-rank fields so that the UI does not lag.
 */
const updateLocusPresetsDebounced = debounce(
  updateLocusPresets,
  CATEGORY_PRESETS_DEBOUNCE_WAIT,
  { leading: true, trailing: true },
)

// Load model data from store when the UUID changes.
watch(
  () => props.locusPresets,
  () => fillData(),
)
// Also, load model data from store when mounted.
onMounted(() => fillData())

// Watch the data and trigger a store update.
watch(data, () => updateLocusPresetsDebounced(), { deep: true })
</script>

<template>
  <h4>Locus Presets &raquo;{{ data?.label ?? 'UNDEFINED' }}&laquo;</h4>
  <v-skeleton-loader v-if="!data" type="article" />
  <v-form v-else ref="formRef">
    <v-text-field
      v-model="data.label"
      :rules="[rules.required]"
      label="Label"
      clearable
      :disabled="readonly"
    />
    <div>
      <v-btn-group variant="outlined" divided>
        <v-btn
          prepend-icon="mdi-arrow-up-circle-outline"
          :disabled="
            props.readonly || data.rank === undefined || data.rank <= 1
          "
          @click="updateLocusPresets(-1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly || data.rank === undefined || data.rank >= maxRank
          "
          @click="updateLocusPresets(1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <v-radio-group v-model="editorToShow" inline class="pt-3">
      <v-radio
        :label="`Gene List (${(data?.genes ?? []).length})`"
        value="genes"
      ></v-radio>
      <v-radio
        :label="`Genomic Regions (${(data?.genome_regions ?? []).length})`"
        value="loci"
      ></v-radio>
    </v-radio-group>

    <div v-if="editorToShow === 'genes'">
      <v-row>
        <v-col>
          <v-textarea
            v-model="genesText"
            :error-messages="genesErrors"
            :hint="genesHint"
            persistent-hint
            label="Enter genes by their symbol, HGNC, ENSEMBL, or Entrez Gene ID, e.g., BRCA1 HGNC:1100 ENSG00000012048 672."
            :disabled="readonly"
            class="mb-3"
          ></v-textarea>

          <v-btn
            block
            variant="outlined"
            text="parse and store regions"
            rounded="xs"
            prepend-icon="mdi-arrow-down-bold"
            :disabled="readonly"
            @click="parseGenes()"
          ></v-btn>

          <div
            class="border-sm rounded bg-surface mt-3 pa-1"
            style="min-height: 100px"
          >
            <span v-for="(gene, idx) in data?.genes ?? []">
              <v-tooltip
                :key="gene.hgnc_id"
                :text="`${gene.symbol} / ${gene.hgnc_id} / ${gene.ensembl_id} / ${gene.entrez_id}`"
                location="bottom"
              >
                <template #activator="{ props }">
                  <v-chip
                    v-bind="props"
                    closable
                    class="ma-1"
                    :text="gene.symbol"
                    :disabled="readonly"
                    @click:close="removeGene(idx)"
                  />
                </template>
              </v-tooltip>
            </span>
          </div>
        </v-col>
      </v-row>
    </div>
    <div v-else>
      <v-row>
        <v-col>
          <v-textarea
            v-model="genomeRegionsText"
            :error-messages="genomeRegionsErrors"
            :hint="genomeRegionsHint"
            persistent-hint
            label="Enter genome regions separated by spaces, e.g., 1 X MT chr1 chr3:1,000,000-2,000,000."
            :disabled="readonly"
            class="mb-3"
          ></v-textarea>

          <v-btn
            block
            variant="outlined"
            text="parse and store regions"
            rounded="xs"
            prepend-icon="mdi-arrow-down-bold"
            :disabled="readonly"
            @click="parseGenomeRegions()"
          ></v-btn>

          <div
            class="border-sm rounded bg-surface mt-3 pa-1"
            style="min-height: 100px"
          >
            <span v-for="(region, idx) in data?.genome_regions ?? []">
              <v-chip
                :key="genomeRegionToString(region)"
                closable
                class="ma-1"
                :text="genomeRegionToString(region)"
                :disabled="readonly"
                @click:close="removeGenomeRegion(idx)"
              />
            </span>
          </div>
        </v-col>
      </v-row>
    </div>
  </v-form>
</template>
