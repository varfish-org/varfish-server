<script setup>
import {
  getGeneSymbol,
  getLinkoutDgv,
  getLinkoutEnsembl,
  getLinkoutEnsemblGene,
  getLinkoutEntrez,
  getLinkoutGenCC,
  getLinkoutGnomad,
  getLinkoutGnomadGene,
  getLinkoutMetaDome,
  getLinkoutMgi,
  getLinkoutMissense3D,
  getLinkoutPubMedPheno,
  getLinkoutUcsc,
  getLinkoutUmd,
  getLinkoutVarseak,
  getLinkoutVarsome,
  getLinkoutMt85,
  getLinkoutMt2021,
} from '@variants/components/VariantDetailsLinkOuts.funcs.js'
import { useFilterQueryStore } from '@variants/stores/filterQuery'

const queryStore = useFilterQueryStore()

const props = defineProps({
  gene: Object,
  smallVariant: Object,
  hgmdProEnabled: Boolean,
  hgmdProPrefix: String,
  umdPredictorApiToken: String,
})
</script>

<template>
  <div class="row">
    <div class="col-12 pl-0 pr-0">
      <strong class="text-muted">Variant @</strong>
      <div class="btn-group btn-group-sm pl-2 mb-2">
        <a
          :href="getLinkoutUcsc(smallVariant)"
          class="btn btn-outline-secondary"
          :class="getLinkoutUcsc(smallVariant) === '#' ? 'disabled' : ''"
          target="_blank"
          >UCSC</a
        >
        <a
          :href="getLinkoutEnsembl(smallVariant)"
          class="btn btn-outline-secondary"
          :class="getLinkoutEnsembl(smallVariant) === '#' ? 'disabled' : ''"
          target="_blank"
          >EnsEMBL</a
        >
        <a
          :href="getLinkoutDgv(smallVariant)"
          class="btn btn-outline-secondary"
          :class="getLinkoutDgv(smallVariant) === '#' ? 'disabled' : ''"
          target="_blank"
          >DGV</a
        >
        <a
          :href="getLinkoutGnomad(smallVariant)"
          class="btn btn-outline-secondary"
          :class="getLinkoutGnomad(smallVariant) === '#' ? 'disabled' : ''"
          target="_blank"
          >gnomAD</a
        >
        <a
          :href="getLinkoutMt85(smallVariant)"
          class="btn btn-outline-secondary"
          :class="getLinkoutMt85(smallVariant) === '#' ? 'disabled' : ''"
          target="_blank"
          >MT 85</a
        >
        <a
          :href="getLinkoutMt2021(smallVariant)"
          class="btn btn-outline-secondary"
          :class="getLinkoutMt2021(smallVariant) === '#' ? 'disabled' : ''"
          target="_blank"
          >MT 2021</a
        >
      </div>
      <strong class="text-muted pl-3">Query @</strong>
      <div class="btn-group btn-group-sm pl-2 mb-2">
        <!-- Todo hgmd pro Linkout -->
        <a class="btn btn-outline-secondary disabled" target="_blank" href="#"
          >Human Splicing Finder</a
        >
        <a
          :href="getLinkoutVarseak(smallVariant, gene)"
          class="btn btn-outline-secondary"
          :class="
            getLinkoutVarseak(smallVariant, gene) === '#' ? 'disabled' : ''
          "
          target="_blank"
          >varSEAK Splicing</a
        >
        <button class="btn btn-sm btn-outline-secondary" :disabled="true">
          PolyPhen2
        </button>
        <a
          :href="getLinkoutUmd(props.umdPredictorApiToken)"
          class="btn btn-outline-secondary"
          :class="props.umdPredictorApiToken ? '' : 'disabled'"
          target="_blank"
          >UMD Predictor</a
        >
      </div>
    </div>
  </div>
</template>
