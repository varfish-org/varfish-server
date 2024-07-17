<script setup lang="ts">
import { SeqvarsQueryPresetsQuality } from '@varfish-org/varfish-api/lib'
import { PropType } from 'vue'

/** The quality presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsQuality>,
})
</script>

<template>
  <h4>Quality Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else>
    <v-checkbox
      v-model="model.filter_active"
      label="Filter Active"
      hide-details
    />

    <div class="text-body-1 pb-3">
      Clear the fields below to remove the filter threshold.
    </div>

    <v-text-field
      v-model="model.min_dp_het"
      label="Min DP Het: minimal depth required for heterozygous genotypes."
      type="number"
      clearable
    />

    <v-text-field
      v-model="model.min_dp_hom"
      label="Min DP Hom: minimal depth required for homozygous genotypes."
      type="number"
      clearable
    />

    <v-text-field
      v-model="model.min_ab_het"
      label="Min AB Het: minimal allelic balance for heterozygous genotypes."
      type="number"
      step="0.01"
      clearable
    />

    <v-text-field
      v-model="model.min_gq"
      label="Min GQ: minimal genotype quality required to pass."
      type="number"
      clearable
    />

    <v-text-field
      v-model="model.min_ad"
      label="Min AD: minimal alternate read depth required to pass."
      type="number"
      clearable
    />

    <v-text-field
      v-model="model.max_ad"
      label="Max AD: maximal alternate read depth allowed to pass."
      type="number"
      clearable
    />
  </v-form>
</template>
