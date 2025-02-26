<script setup lang="ts">
/**
 * This component allows to edit the per-sample quality presets.
 *
 * The component is passed the current seqvar query for editing and updates
 * it via TanStack Query.
 */
import {
  GenePydanticList,
  SeqvarsQueryDetails,
  SeqvarsQuerySettingsLocus,
} from '@varfish-org/varfish-api/lib'
import { isDeepEqual, partition, uniqueWith } from 'remeda'
import { computed, ref, watch } from 'vue'

import {
  genomeRegionToString,
  parseGenomeRegion,
} from '@/seqvars/components/PresetsEditor/lib'
import { useSeqvarQueryUpdateMutation } from '@/seqvars/queries/seqvarQuery'
import { AnnonarsApiClient, GeneNames } from '@/varfish/api/annonars'
import { useCtxStore } from '@/varfish/stores/ctx'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** The query that is to be edited. */
    modelValue: SeqvarsQueryDetails
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

/**
 * Mutation for updating a seqvar query.
 *
 * This is done via TanStack Query which uses optimistic updates for quick
 * reflection in the UI.
 */
const seqvarQueryUpdate = useSeqvarQueryUpdateMutation()

/**
 * Helper to apply a patch to the current `props.modelValue`.
 */
const applyMutation = async (locus: SeqvarsQuerySettingsLocus) => {
  const newData = {
    ...props.modelValue,
    settings: {
      ...props.modelValue.settings,
      locus: {
        ...props.modelValue.settings.locus,
        ...locus,
      },
    },
  }

  // Apply update via TanStack query; will use optimistic updates for quick
  // reflection in the UI.
  await seqvarQueryUpdate.mutateAsync({
    body: newData,
    path: {
      session: props.modelValue.session,
      query: props.modelValue.sodar_uuid,
    },
  })
}

const hasGenes = computed(
  () => props.modelValue.settings.locus.genes!.length > 0,
)

const choice = ref<keyof typeof props.modelValue.settings.locus>(
  hasGenes.value ? 'genes' : 'genome_regions',
)

const LABEL_REGIONS =
  'Space-separated genome regions, e.g., 1 X MT chr1 chr3:1,000,000-2,000,000.'
const LABEL_GENES =
  'Space-separated symbols, HGNC, ENSEMBL, or Entrez ID, e.g., BRCA1 HGNC:1100 ENSG00000012048 672.'

const showDialog = ref<boolean>(false)
const textAreaValue = ref('')
const textAreaErrorMessages = ref<string[]>([])
const parsing = ref(false)

watch(choice, async (choiceValue) => {
  textAreaErrorMessages.value = []

  if (choiceValue == 'genes') {
    await applyMutation({
      ...props.modelValue.settings.locus,
      genome_regions: [],
    })
  } else {
    await applyMutation({ ...props.modelValue.settings.locus, genes: [] })
  }
})

const parseAndStore = async () => {
  parsing.value = true

  const words = textAreaValue.value.split(/[;\s+]/).filter((s) => s.trim())

  if (choice.value == 'genome_regions') {
    const results = words.map((text) => {
      try {
        return parseGenomeRegion(text)
      } catch (error) {
        return { text, message: (error as Error).message }
      }
    })
    const [regions, errors] = partition(results, (v) => 'chromosome' in v)
    await applyMutation({
      ...props.modelValue.settings.locus,
      genome_regions: uniqueWith(
        [...(props.modelValue.settings.locus.genome_regions ?? []), ...regions],
        isDeepEqual,
      ),
    })
    textAreaValue.value = errors.map((e) => e.text).join('\n')
    textAreaErrorMessages.value = errors.map((e) => e.message)
  } else {
    /** Store with application context, such as CSRF token. */
    const ctxStore = useCtxStore()
    // Annonars client to use.
    const annonarsClient = new AnnonarsApiClient(ctxStore.csrfToken)

    // Lookup genes with annonars, add to data and/or generate error message.
    const foundGenes = await annonarsClient.lookupGenes(words)

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
    // Collect list of already present identifiers.
    for (const gene of props.modelValue.settings.locus.genes ?? []) {
      registerIdentifier(
        { ...gene, name: gene.symbol!, alias_name: [], alias_symbol: [] },
        seen,
      )
    }

    /** Helper type to unpack, e.g., `Array<T1 | T2>`. */
    type _Unpacked<T> = T extends (infer U)[] ? U : T

    // Copy-convert the found genes over to the data, removing duplicates.
    const genes = new Array<_Unpacked<GenePydanticList>>()
    genes.push(...(props.modelValue.settings.locus.genes ?? []))
    const alreadyAdded = new Set<string>()
    for (const gene of foundGenes) {
      if (
        alreadyAdded.has(gene.hgnc_id) ||
        alreadyAdded.has(gene.symbol) ||
        (gene.ensembl_gene_id && alreadyAdded.has(gene.ensembl_gene_id)) ||
        (gene.ncbi_gene_id && alreadyAdded.has(gene.ncbi_gene_id))
      ) {
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
    await applyMutation({
      ...props.modelValue.settings.locus,
      genes,
    })

    // Copy the genes that were not found over back to the text area.
    const invalidGenes: string[] = []
    for (const gene of words) {
      if (!seen.has(gene)) {
        invalidGenes.push(gene)
      }
    }
    textAreaErrorMessages.value =
      invalidGenes.length > 0 ? ['Some genes could not be found.'] : []
    textAreaValue.value = invalidGenes.join(' ')
  }
  parsing.value = false
}
</script>

<template>
  <v-sheet class="pr-1 pt-1 mb-1 bg-transparent">
    <div class="d-flex align-center justify-space-between ga-4">
      <span class="text-caption text-uppercase pb-1">
        <template v-if="modelValue.settings.locus.genes?.length">
          Gene List
        </template>
        <template v-else-if="modelValue.settings.locus.genome_regions?.length">
          Genome Regions
        </template>
        <template v-else> Gene List / Genome Regions </template>
      </span>

      <div>
        <v-btn
          v-if="
            !!modelValue.settings.locus.genes?.length ||
            !!modelValue.settings.locus.genome_regions?.length
          "
          size="small"
          density="compact"
          variant="plain"
          prepend-icon="mdi-close-circle-multiple"
          text="Clear"
          class="pr-2"
          @click="
            async () =>
              await applyMutation({
                ...modelValue.settings.locus,
                genes: [],
                genome_regions: [],
              })
          "
        />
        <v-btn
          size="small"
          density="compact"
          variant="plain"
          prepend-icon="mdi-tune-variant"
          text="Edit"
          class="px-1"
          @click="showDialog = true"
        />
      </div>
    </div>

    <div>
      <template v-if="modelValue.settings.locus.genes?.length">
        <v-chip
          v-for="(item, index) in modelValue.settings.locus.genes"
          :key="item.hgnc_id"
          size="small"
          class="mr-1 mb-1"
          closable
          @click:close="
            async () =>
              await applyMutation({
                ...modelValue.settings.locus,
                genes: modelValue.settings.locus.genes?.filter(
                  (_, i) => i !== index,
                ),
              })
          "
        >
          {{ item.symbol }}
        </v-chip>
      </template>

      <template v-else-if="modelValue.settings.locus.genome_regions?.length">
        <v-chip
          v-for="(item, index) in modelValue.settings.locus.genome_regions"
          :key="genomeRegionToString(item)"
          size="small"
          class="mr-1 mb-1"
          closable
          @click:close="
            async () =>
              await applyMutation({
                ...modelValue.settings.locus,
                genome_regions:
                  modelValue.settings.locus.genome_regions?.filter(
                    (_, i) => i !== index,
                  ),
              })
          "
        >
          {{ genomeRegionToString(item) }}
        </v-chip>
      </template>

      <template v-else>
        <div
          class="text-caption text-center font-italic text-grey-darken-2 py-1"
        >
          None Selected
        </div>
      </template>
    </div>
  </v-sheet>

  <v-dialog v-model="showDialog" max-width="600">
    <template #default>
      <v-card title="Edit Genes / Genome Regions">
        <v-card-text class="d-flex flex-column ga-2">
          <v-radio-group v-model="choice" inline :hide-details="true">
            <v-radio label="Gene list" value="genes" />
            <v-radio label="Genome regions" value="genome_regions" />
          </v-radio-group>

          <v-textarea
            v-model="textAreaValue"
            :label="choice == 'genome_regions' ? LABEL_REGIONS : LABEL_GENES"
            :hide-details="textAreaErrorMessages.length == 0"
            :error="textAreaErrorMessages.length > 0"
            :messages="textAreaErrorMessages"
            :disabled="parsing"
            variant="outlined"
          />

          <v-btn
            text="Parse and store"
            :loading="parsing"
            :disabled="parsing"
            @click="parseAndStore"
          />

          <v-sheet class="border-sm border-black px-2 pt-2 pb-1">
            <template
              v-if="
                !!modelValue.settings.locus.genes?.length ||
                !!modelValue.settings.locus.genome_regions?.length
              "
            >
              <v-chip
                v-for="(item, index) in choice == 'genes'
                  ? modelValue.settings.locus.genes
                  : modelValue.settings.locus.genome_regions"
                :key="index"
                size="small"
                closable
                class="mr-1 mb-1"
                @click:close="
                  (choice == 'genes'
                    ? modelValue.settings.locus.genes
                    : modelValue.settings.locus.genome_regions
                  )?.splice(index, 1)
                "
              >
                {{
                  'chromosome' in item
                    ? genomeRegionToString(item)
                    : item.symbol
                }}
              </v-chip>
            </template>
            <template v-else>
              <div
                class="text-body-2 text-center font-italic text-grey-darken-2 py-1"
              >
                None Selected
              </div>
            </template>
          </v-sheet>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn text="Close Dialog" @click="showDialog = false" />
        </v-card-actions>
      </v-card>
    </template>
  </v-dialog>
</template>
