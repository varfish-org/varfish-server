<script setup lang="ts">
import { SeqvarsQueryPresetsLocus } from '@varfish-org/varfish-api/lib'
import { PropType, ref } from 'vue'

/** The locus presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsLocus>,
})

/** Whether to show editor for genes or loci; component state. */
const editorToShow = ref<'genes' | 'loci'>(
  model.value.genes.length > 0 ? 'genes' : 'loci'
)

/** Genomic regions text area; component state */
const genomicRegionsText = ref<string>('')
</script>

<template>
  <h4>Locus Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else>
    <v-radio-group
      v-model="editorToShow"
      inline
    >
      <v-radio
        label="Gene List"
        value="genes"
      ></v-radio>
      <v-radio
        label="Genomic Regions"
        value="loci"
      ></v-radio>
    </v-radio-group>

    <div v-if="editorToShow === 'genes'">
      Genes
    </div>
    <div v-else>
      <v-row>
        <v-col cols="6">
          <v-textarea
            :model-value="genomicRegionsText"
            label="Enter genomic regions, e.g., 1, X, MT, chr1, chr3:1,000,000-2,000,000."
          ></v-textarea>
        </v-col>
        <v-col cols="6">
          <v-btn block variant="outlined" label="xxx" rounded="xs" prepend-icon="mdi-arrow-down-bold"></v-btn>
        </v-col>
      </v-row>
    </div>
  </v-form>
</template>
