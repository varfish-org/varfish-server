<script setup lang="ts">
import { SeqvarsQueryPresetsLocus } from '@varfish-org/varfish-api/lib'
import { genomeRegionToString, GenomeRegion, parseGenomeRegion } from './lib'
import { PropType, ref } from 'vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether the editor is readonly. */
    readonly: boolean
  }>(),
  { readonly: false },
)

/** The locus presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsLocus>,
})

/** Whether to show editor for genes or loci; component state. */
const editorToShow = ref<'genes' | 'loci'>(
  (model.value?.genes?.length ?? 0) > 0 ? 'genes' : 'loci',
)

/** Genome regions text area; component state. */
const genomeRegionsText = ref<string>('')

/** Error message(s) for genome regions; component state. */
const genomeRegionsErrors = ref<string>('')
/** Hint(s) for genome regions; component state. */
const genomeRegionsHint = ref<string>('')

/** Handler for parsing genomic regions on clicking the button. */
const parseGenomeRegions = async () => {
  // Clear any error message and hints.
  genomeRegionsErrors.value = ''
  genomeRegionsHint.value = ''

  // Guard against empty model or genome regions.
  if (model?.value?.genome_regions?.length === undefined) {
    genomeRegionsErrors.value = 'Invalid model state (should never happen)'
    return
  }
  // Get genome regions string from text area.
  const genomeRegionsArr = genomeRegionsText.value
    .split(/[;\s+]/)
    .filter((r) => r.length > 0)
  // Loop over genome regions, parse it, add to model and/or generate error message.
  const invalidGenomeRegions: string[] = []
  for (const genomeRegion of genomeRegionsArr) {
    try {
      const parsed = parseGenomeRegion(genomeRegion)
      // Only add to model if not already present; this also ensures that
      // the text description is unique and can be used as `:key` below.
      if (
        !model.value.genome_regions.find(
          (r: GenomeRegion) =>
            genomeRegionToString(r) === genomeRegionToString(parsed),
        )
      ) {
        model.value.genome_regions.push(parsed)
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

/** Handler for removing genome region from model on clicking "close" in chip. */
const removeGenomeRegion = async (index: number) => {
  // Guard against empty model or genome regions.
  if (!model?.value?.genome_regions?.length) {
    return
  }
  // Remove genome region from model by index.
  model.value.genome_regions.splice(index, 1)
}
</script>

<template>
  <h4>Locus Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h4>
  <v-skeleton-loader v-if="!model" type="article" />
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
            v-model="genomeRegionsText"
            :error-messages="genomeRegionsErrors"
            :hint="genomeRegionsHint"
            persistent-hint
            label="Enter genome regions separated by spaces, e.g., 1 X MT chr1 chr3:1,000,000-2,000,000."
            :disabled="readonly"
          ></v-textarea>
        </v-col>
        <v-col cols="6" class="d-flex flex-column">
          <v-btn
            block
            variant="outlined"
            text="parse and store regions"
            rounded="xs"
            prepend-icon="mdi-arrow-down-bold"
            :disabled="readonly"
            @click="parseGenomeRegions()"
          ></v-btn>
          <div class="border-sm rounded h-100 bg-surface mt-3 pa-1">
            <span v-for="(region, idx) in model?.genome_regions ?? []">
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
