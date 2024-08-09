<script setup lang="ts">
import { isDeepEqual, partition, uniqueWith } from 'remeda'
import { computed, ref, watch } from 'vue'

import { Query } from '@/seqvars/types'
import {
  parseGenomeRegion,
  genomeRegionToString,
} from '@/seqvars/components/PresetsEditor/lib'
import { useCtxStore } from '@/varfish/stores/ctx'
import { AnnonarsApiClient, GeneNames } from '@/varfish/api/annonars'
import { GenePydanticList } from '@varfish-org/varfish-api/lib'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

const model = defineModel<Query>({ required: true })
const hasGenes = computed(() => model.value.locus.genes!.length > 0)

const choice = ref<keyof typeof model.value.locus>(
  hasGenes.value ? 'genes' : 'genome_regions',
)

const textAreaValue = ref('')
const textAreaErrorMessages = ref<string[]>([])
const parsing = ref(false)

watch(choice, (choiceValue) => {
  textAreaErrorMessages.value = []

  if (choiceValue == 'genes') {
    model.value.locus.genome_regions = []
  } else {
    model.value.locus.genes = []
  }
})

async function parseAndStore() {
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
    model.value.locus.genome_regions = uniqueWith(
      [...(model.value.locus.genome_regions ?? []), ...regions],
      isDeepEqual,
    )
    textAreaValue.value = errors.map((e) => e.text).join('\n')
    textAreaErrorMessages.value = errors.map((e) => e.message)
  } else {
    /** Store with application context, such as CSRF token. */
    const ctxStore = useCtxStore()
    // Annonars client to use.
    const annonarsClient = new AnnonarsApiClient(ctxStore.csrfToken)

    // Lookup genes with annonars, add to data and/or generate error message.
    const foundGenes = await annonarsClient.lookupGenes(words)
    console.log(foundGenes)

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
    for (const gene of model.value.locus.genes ?? []) {
      registerIdentifier(
        { ...gene, name: gene.symbol!, alias_name: [], alias_symbol: [] },
        seen,
      )
    }

    /** Helper type to unpack, e.g., `Array<T1 | T2>`. */
    type _Unpacked<T> = T extends (infer U)[] ? U : T

    // Copy-convert the found genes over to the data, removing duplicates.
    const genes = new Array<_Unpacked<GenePydanticList>>()
    genes.push(...(model.value.locus.genes ?? []))
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
    model.value.locus.genes = genes

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
  <v-dialog max-width="500">
    <template #activator="{ props: activatorProps }">
      <div
        style="
          margin-top: 4px;
          display: flex;
          gap: 4px;
          align-items: center;
          justify-content: space-between;
        "
      >
        {{ hasGenes ? 'Gene List' : 'Genome Regions' }}
        <v-btn
          size="small"
          density="compact"
          variant="plain"
          prepend-icon="mdi-tune-variant"
          v-bind="activatorProps"
          text="Edit"
        />
      </div>
    </template>

    <template #default="{ isActive }">
      <v-card title="Locus Configuration">
        <v-card-text style="display: flex; flex-direction: column; gap: 8px">
          <v-radio-group v-model="choice" inline :hide-details="true">
            <v-radio label="Gene list" value="genes" />
            <v-radio label="Genomic regions" value="genome_regions" />
          </v-radio-group>

          <v-textarea
            v-model="textAreaValue"
            :label="choice == 'genome_regions' ? 'Regions' : 'Genes'"
            :hide-details="textAreaErrorMessages.length == 0"
            :error="textAreaErrorMessages.length > 0"
            :messages="textAreaErrorMessages"
            :disabled="parsing"
          />

          <v-btn
            text="Parse and store"
            :loading="parsing"
            :disabled="parsing"
            @click="parseAndStore"
          />

          <div style="display: flex; gap: 4px; flex-wrap: wrap">
            <v-chip
              v-for="(item, index) in choice == 'genes'
                ? model.locus.genes
                : model.locus.genome_regions"
              :key="index"
              size="small"
              closable
              @click:close="
                (choice == 'genes'
                  ? model.locus.genes
                  : model.locus.genome_regions
                )?.splice(index, 1)
              "
            >
              {{
                'chromosome' in item ? genomeRegionToString(item) : item.symbol
              }}
            </v-chip>
          </div>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn text="Close Dialog" @click="isActive.value = false" />
        </v-card-actions>
      </v-card>
    </template>
  </v-dialog>

  <div style="max-width: 280px; display: flex; gap: 4px; flex-wrap: wrap">
    <v-chip
      v-for="(item, index) in hasGenes
        ? model.locus.genes
        : model.locus.genome_regions"
      :key="index"
      size="small"
    >
      {{ 'chromosome' in item ? genomeRegionToString(item) : item.symbol }}
    </v-chip>
  </div>
</template>
