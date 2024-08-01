<script setup lang="ts">
import { isDeepEqual, partition, uniqueWith } from 'remeda'
import { computed, ref, watch } from 'vue'

import { Query } from '@/seqvars/types'
import { queryHPO_Terms } from '../utils'
import { parseGenomeRegion } from './genome-region'
import { genomeRegionToString } from './genome-region'

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
    const results = await Promise.all(
      words.map(async (word) => {
        const results = await queryHPO_Terms(word)
        return results.at(0) ?? { missing: word }
      }),
    )
    const [genes, missing] = partition(results, (v) => 'label' in v)
    model.value.locus.genes = genes.map((g) => ({
      hgnc_id: g.term_id,
      symbol: g.label,
    }))
    textAreaValue.value = missing.map((m) => m.missing).join('\n')
    textAreaErrorMessages.value = missing.length > 0 ? ['No results'] : []
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
        {{ hasGenes ? 'Gene List' : 'Gene Regions' }}
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
                'chromosome' in item ? genomeRegionToString(item) : item.hgnc_id
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
      {{ 'chromosome' in item ? genomeRegionToString(item) : item.hgnc_id }}
    </v-chip>
  </div>
</template>
