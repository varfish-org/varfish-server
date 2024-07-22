<script setup lang="ts">
import { SeqvarsQueryPresetsLocus } from '@varfish-org/varfish-api/lib'
import { genomeRegionToString, GenomeRegion } from './lib'
import { PropType, ref } from 'vue'

/** The locus presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsLocus>,
})

/** Whether to show editor for genes or loci; component state. */
const editorToShow = ref<'genes' | 'loci'>(
  (model.value?.genes?.length ?? 0) > 0 ? 'genes' : 'loci',
)

/** Genomic regions text area; component state. */
const genomicRegionsText = ref<string>('')

/** Validation rules for genome regions */
const genomicRegionsRules = [
  (v: string) => {
    if (!v) {
      return 'Genomic regions are required.'
    }
    return true
  },
]

/**
 * Parse genomic regions from text area and put into model.
 */
const parseGenomicRegions = async () => {
  // Guard against empty text area.
  if (!genomicRegionsText.value) {
    return
  }
  // Split text area content by spaces.
  const regions = genomicRegionsText.value.split(/\s+/)
  // Loop over regions, try to parse, and add to model.
}

/** Handler for removing genome region from model. */
const removeGenomeRegion = async (region: GenomeRegion) => {
  // Guard against empty model or genome regions.
  if (!model?.value?.genome_regions?.length) {
    return
  }
  // Remove genome region from model by string representation.
  model.value.genome_regions = model.value.genome_regions.filter(
    (r: GenomeRegion) =>
      genomeRegionToString(r) !== genomeRegionToString(region),
  )
}
</script>

<template>
  <h4>Locus Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else>
    <v-radio-group v-model="editorToShow" inline>
      <v-radio label="Gene List" value="genes"></v-radio>
      <v-radio label="Genomic Regions" value="loci"></v-radio>
    </v-radio-group>

    <div v-if="editorToShow === 'genes'">Genes</div>
    <div v-else>
      <v-row>
        <v-col cols="6">
          <v-textarea
            :model-value="genomicRegionsText"
            :rules="genomicRegionsRules"
            label="Enter genomic regions separated by spaces, e.g., 1 X MT chr1 chr3:1,000,000-2,000,000."
          ></v-textarea>
        </v-col>
        <v-col cols="6" class="d-flex flex-column">
          <v-btn
            block
            variant="outlined"
            text="xxx"
            rounded="xs"
            prepend-icon="mdi-arrow-down-bold"
          ></v-btn>
          <div class="border-sm rounded h-100 bg-surface mt-3">
            <v-chip
              v-for="region in model?.genome_regions ?? []"
              :key="genomeRegionToString(region)"
              close
              @click:close="removeGenomeRegion(region)"
            >
              {{ genomeRegionToString(region) }}
            </v-chip>
          </div>
        </v-col>
      </v-row>
    </div>
  </v-form>
</template>
