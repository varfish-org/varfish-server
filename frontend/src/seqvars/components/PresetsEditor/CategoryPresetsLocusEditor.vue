<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { SeqvarsQueryPresetsLocus } from '@varfish-org/varfish-api/lib'
import { data } from 'jquery'
import { computed, ref } from 'vue'
import { VForm } from 'vuetify/lib/components/index.mjs'

import {
  invalidateSeqvarQueryPresetsSetVersionKeys,
  useSeqvarQueryPresetsSetVersionRetrieveQuery,
} from '@/seqvars/queries/seqvarQueryPresetSetVersion'
import {
  useSeqvarsQueryPresetsLocusRetrieveQuery,
  useSeqvarsQueryPresetsLocusUpdateMutation,
} from '@/seqvars/queries/seqvarQueryPresetsLocus'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'
import { AnnonarsApiClient, GeneNames } from '@/varfish/api/annonars'
import { useCtxStore } from '@/varfish/stores/ctx'

import { GenomeRegion, genomeRegionToString, parseGenomeRegion } from './lib'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** UUID of the current presets set. */
    presetSet?: string
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

/** The `QueryClient` for explicit invalidation.*/
const queryClient = useQueryClient()

/** Presets set UUID as `ComputedRef` for queries. */
const presetsSetUuid = computed<string | undefined>(() => {
  return props.presetSet
})
/** Presets set version UUID as `ComputedRef` for queries. */
const presetsSetVersionUuid = computed<string | undefined>(() => {
  return props.presetSetVersion
})
/** Locus presets UUID as `ComputedRef` for queries. */
const presetsLocusUuid = computed<string | undefined>(() => {
  return props.locusPresets
})

/** Query with the currently selected presets set version. */
const presetsSetVersionRetrieveRes =
  useSeqvarQueryPresetsSetVersionRetrieveQuery({
    presetsSetUuid,
    presetsSetVersionUuid,
  })
/** Query with the currently selected locus presets. */
const presetsLocusRetrieveRes = useSeqvarsQueryPresetsLocusRetrieveQuery({
  presetsSetVersionUuid,
  presetsLocusUuid,
})
/** Mutation for updating the locus presets. */
const locusPresetsUpdate = useSeqvarsQueryPresetsLocusUpdateMutation()

/** Shortcut to the number of locus presets, used for rank. */
const maxRank = computed<number>(
  () =>
    presetsSetVersionRetrieveRes.data.value?.seqvarsquerypresetslocus_set
      .length ?? 0,
)

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
  (presetsLocusRetrieveRes.data.value?.genes?.length ?? 0) > 0
    ? 'genes'
    : 'loci',
)

/** Handler for parsing genes on clicking the button; using the annonars API. */
const parseGenes = async () => {
  // Annonars client to use.
  const annonarsClient = new AnnonarsApiClient(ctxStore.csrfToken)

  // Clear any error message and hints.
  genesErrors.value = ''
  genesHint.value = ''

  // Guard against empty data or genome regions.
  if (presetsLocusRetrieveRes.data?.value?.genes?.length === undefined) {
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

  // New array of genes.
  const genes = [...presetsLocusRetrieveRes.data.value.genes]

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

    genes.push({
      hgnc_id: gene.hgnc_id,
      symbol: gene.symbol,
      name: gene.name,
      ensembl_id: gene.ensembl_gene_id ?? undefined,
      entrez_id: gene.ncbi_gene_id ? parseInt(gene.ncbi_gene_id) : undefined,
    })
  }

  // Helpfully, sort genes by symbol.
  genes.sort((a, b) => a.symbol.localeCompare(b.symbol))
  // Update list in the presets on the server.
  await applyMutation({
    genes,
  })

  // Copy the genes that were not found over back to the text area.
  const invalidGenes: string[] = []
  for (const gene of genesArr) {
    if (!seen.has(gene)) {
      invalidGenes.push(gene)
    }
  }
  if (invalidGenes.length > 0) {
    genesErrors.value = 'Some genes could not be found.'
  }
  genesText.value = invalidGenes.join(' ')
}

/** Handler for removing genes from data on clicking "close" in chip. */
const removeGene = async (index: number) => {
  // Guard against empty data or genome regions.
  if (!presetsLocusRetrieveRes.data?.value?.genes?.length) {
    return
  }
  // New array of genes.
  const genes = [...presetsLocusRetrieveRes.data.value.genes]
  genes.splice(index, 1)
  // Update list in the presets on the server.
  await applyMutation({
    genes,
  })
}

/** Handler for parsing genomic regions on clicking the button. */
const parseGenomeRegions = async () => {
  // Clear any error message and hints.
  genomeRegionsErrors.value = ''
  genomeRegionsHint.value = ''

  // Guard against empty data or genome regions.
  if (
    presetsLocusRetrieveRes.data?.value?.genome_regions?.length === undefined
  ) {
    genomeRegionsErrors.value = 'Invalid data state (should never happen)'
    return
  }
  // Get genome regions string from text area.
  const genomeRegionsArr = genomeRegionsText.value
    .split(/[;\s+]/)
    .filter((r) => r.length > 0)
  // Loop over genome regions, parse it, add to data and/or generate error message.
  const genomeRegions = [...presetsLocusRetrieveRes.data.value.genome_regions]
  const invalidGenomeRegions: string[] = []
  for (const genomeRegion of genomeRegionsArr) {
    try {
      const parsed = parseGenomeRegion(genomeRegion)
      // Only add to data if not already present; this also ensures that
      // the text description is unique and can be used as `:key` below.
      if (
        !genomeRegions.find(
          (r: GenomeRegion) =>
            genomeRegionToString(r) === genomeRegionToString(parsed),
        )
      ) {
        genomeRegions.push(parsed)
      } else {
        genomeRegionsHint.value = 'Skipped already present genome regions.'
      }
    } catch (e) {
      invalidGenomeRegions.push(genomeRegion)
    }
  }
  // Update list in the presets on the server.
  await applyMutation({
    genome_regions: genomeRegions,
  })
  if (invalidGenomeRegions.length > 0) {
    genomeRegionsErrors.value = 'Some genome regions could not be parsed.'
  }
  genomeRegionsText.value = invalidGenomeRegions.join(' ')
}

/** Handler for removing genome region from data on clicking "close" in chip. */
const removeGenomeRegion = async (index: number) => {
  // Guard against empty data or genome regions.
  if (!presetsLocusRetrieveRes.data?.value?.genome_regions?.length) {
    return
  }
  // New array of genome regions.
  const genomeRegions = [...presetsLocusRetrieveRes.data.value.genome_regions]
  genomeRegions.splice(index, 1)
  // Update list in the presets on the server.
  await applyMutation({
    genome_regions: genomeRegions,
  })
}

/** Helper to apply a patch to the current `presetsLocusRetrieveRes.data.value`. */
const applyMutation = async (
  patch: Partial<SeqvarsQueryPresetsLocus>,
  rankDelta: number = 0,
) => {
  // Guard against invalid form data.
  const validateResult = await formRef.value?.validate()
  if (validateResult?.valid !== true) {
    return
  }
  // Short-circuit if patch is undefined or presets version undefine dor not in draft state.
  if (
    props.presetSet === undefined ||
    props.presetSetVersion === undefined ||
    presetsLocusRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value.status !==
      PresetSetVersionState.DRAFT
  ) {
    return
  } else {
    patch.rank = presetsLocusRetrieveRes.data.value.rank
  }

  // Helper to update the rank of the other item as well.
  const updateOtherItemRank = async () => {
    if (props.presetSetVersion !== undefined && rankDelta !== 0) {
      const version = presetsSetVersionRetrieveRes.data.value
      if (
        version === undefined ||
        patch.rank === undefined ||
        patch.rank + rankDelta < 1 ||
        patch.rank + rankDelta > maxRank.value
      ) {
        // Guard against invalid or missing data.
        return
      }
      // Find the next smaller or larger item, sort by rank.
      const others = version.seqvarsquerypresetslocus_set.filter((elem) => {
        if (elem.sodar_uuid === props.locusPresets) {
          return false
        }
        if (rankDelta < 0) {
          return (elem.rank ?? 0) < (patch?.rank ?? 0)
        } else {
          return (elem.rank ?? 0) > (patch?.rank ?? 0)
        }
      })
      others.sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
      // Then, pick the other item to flip ranks with.
      const other = { ...others[rankDelta < 0 ? others.length - 1 : 0] }
      // Store the other's rank in `data.rank` and update other via API.
      if (!!other) {
        const newOtherRank = patch.rank
        patch.rank = other.rank
        other.rank = newOtherRank
        try {
          await locusPresetsUpdate.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetslocus: other.sodar_uuid,
            },
            body: {
              ...other,
              rank: newOtherRank,
            },
          })
        } catch (error) {
          emit('message', {
            text: `Failed to update other locus presets rank: ${error}`,
            color: 'error',
          })
        }
      }
    }
  }

  // First, apply rank update to other data object and to patch if applicable.
  // On success, the patch to the data object.
  try {
    await updateOtherItemRank()
    await locusPresetsUpdate.mutateAsync({
      path: {
        querypresetssetversion: props.presetSetVersion,
        querypresetslocus: presetsLocusRetrieveRes.data.value.sodar_uuid,
      },
      body: {
        ...presetsLocusRetrieveRes.data.value,
        ...patch,
      },
    })
    // Explicitely invalidate the query presets set version as the title and rank
    // can change and the version stores the category presets as well.
    invalidateSeqvarQueryPresetsSetVersionKeys(queryClient, {
      querypresetsset: props.presetSet,
      querypresetssetversion: props.presetSetVersion,
    })
  } catch (error) {
    emit('message', {
      text: `Failed to update locus presets: ${error}`,
      color: 'error',
    })
  }
}
</script>

<template>
  <h3>
    Locus Presets &raquo;{{
      presetsLocusRetrieveRes.data.value?.label ?? 'UNDEFINED'
    }}&laquo;
  </h3>

  <v-skeleton-loader v-if="!data" type="article" />
  <v-form v-else ref="formRef">
    <v-text-field
      :model-value="presetsLocusRetrieveRes.data.value?.label"
      :rules="[rules.required]"
      label="Label"
      clearable
      :disabled="readonly"
      @update:model-value="
        (label) =>
          applyMutation({
            label,
          })
      "
    />

    <div>
      <v-btn-group variant="outlined" divided>
        <v-btn
          prepend-icon="mdi-arrow-up-circle-outline"
          :disabled="
            props.readonly ||
            presetsLocusRetrieveRes.data.value?.rank === undefined ||
            presetsLocusRetrieveRes.data.value?.rank <= 1
          "
          @click="applyMutation({}, -1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly ||
            presetsLocusRetrieveRes.data.value?.rank === undefined ||
            presetsLocusRetrieveRes.data.value?.rank >= maxRank
          "
          @click="applyMutation({}, 1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <v-radio-group v-model="editorToShow" inline class="pt-3">
      <v-radio
        :label="`Gene List (${(presetsLocusRetrieveRes.data.value?.genes ?? []).length})`"
        value="genes"
      ></v-radio>
      <v-radio
        :label="`Genomic Regions (${(presetsLocusRetrieveRes.data.value?.genome_regions ?? []).length})`"
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
            <span
              v-for="(gene, idx) in presetsLocusRetrieveRes.data.value?.genes ??
              []"
            >
              <v-tooltip
                :key="gene.hgnc_id"
                :text="`${gene.symbol} / ${gene.hgnc_id} / ${gene.ensembl_id} / ${gene.entrez_id}`"
                location="bottom"
              >
                <template #activator="{ props: innerProps }">
                  <v-chip
                    v-bind="innerProps"
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
            <span
              v-for="(region, idx) in presetsLocusRetrieveRes.data.value
                ?.genome_regions ?? []"
            >
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
