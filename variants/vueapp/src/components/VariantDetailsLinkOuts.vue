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
  getLinkoutVariantValidator,
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
      <strong class="text-muted">Gene @</strong>
      <div class="btn-group btn-group-sm pl-2 mb-2">
        <a
          :href="'https://www.omim.org/search/?search=' + getGeneSymbol(gene)"
          class="btn btn-outline-secondary"
          :class="getGeneSymbol(gene) ? '' : 'disabled'"
          target="_blank"
          >OMIM</a
        >
        <a
          :href="
            'https://www.genecards.org/cgi-bin/carddisp.pl?gene=' +
            getGeneSymbol(gene)
          "
          class="btn btn-outline-secondary"
          :class="getGeneSymbol(gene) ? '' : 'disabled'"
          target="_blank"
          >GeneCards</a
        >
        <a
          :href="getLinkoutEntrez(gene)"
          class="btn btn-outline-secondary"
          :class="getLinkoutEntrez(gene) === '#' ? 'disabled' : ''"
          target="_blank"
          >Entrez</a
        >
        <a
          :href="
            'https://www.genenames.org/cgi-bin/gene_symbol_report?match=' +
            getGeneSymbol(gene)
          "
          class="btn btn-outline-secondary"
          :class="getGeneSymbol(gene) ? '' : 'disabled'"
          target="_blank"
          >HGNC</a
        >
        <a
          :href="
            'http://www.hgmd.cf.ac.uk/ac/gene.php?gene=' + getGeneSymbol(gene)
          "
          class="btn btn-outline-secondary"
          :class="getGeneSymbol(gene) ? '' : 'disabled'"
          target="_blank"
          >HGMD Public</a
        >
        <a
          :href="'https://www.proteinatlas.org/search/' + getGeneSymbol(gene)"
          class="btn btn-outline-secondary"
          :class="getGeneSymbol(gene) ? '' : 'disabled'"
          target="_blank"
          >ProteinAtlas</a
        >
        <a
          :href="
            'https://www.ncbi.nlm.nih.gov/pubmed/?term=' + getGeneSymbol(gene)
          "
          class="btn btn-outline-secondary"
          :class="getGeneSymbol(gene) ? '' : 'disabled'"
          target="_blank"
          >PubMed</a
        >
        <a
          :href="
            'https://www.ncbi.nlm.nih.gov/clinvar/?term=' + getGeneSymbol(gene)
          "
          class="btn btn-outline-secondary"
          :class="getGeneSymbol(gene) ? '' : 'disabled'"
          target="_blank"
          >ClinVar</a
        >
        <a
          :href="
            'https://panelapp.genomicsengland.co.uk/panels/entities/' +
            getGeneSymbol(gene)
          "
          class="btn btn-outline-secondary"
          :class="getGeneSymbol(gene) ? '' : 'disabled'"
          target="_blank"
          >PanelApp</a
        >
        <a
          v-if="props.hgmdProEnabled"
          :href="props.hgmdProPrefix + '/gene.php?gene=' + getGeneSymbol(gene)"
          class="btn btn-outline-secondary"
          :class="getGeneSymbol(gene) ? '' : 'disabled'"
          target="_blank"
          >HGMD Pro</a
        >
        <a
          :href="getLinkoutEnsemblGene(smallVariant)"
          class="btn btn-outline-secondary"
          :class="getLinkoutEnsemblGene(smallVariant) === '#' ? 'disabled' : ''"
          target="_blank"
          >EnsEMBL</a
        >
        <a
          :href="getLinkoutMetaDome(smallVariant)"
          class="btn btn-outline-secondary"
          :class="getLinkoutMetaDome(smallVariant) === '#' ? 'disabled' : ''"
          target="_blank"
          >MetaDome</a
        >
        <a
          :href="getLinkoutGnomadGene(smallVariant)"
          class="btn btn-outline-secondary"
          :class="getLinkoutGnomadGene(smallVariant) === '#' ? 'disabled' : ''"
          target="_blank"
          >gnomAD</a
        >
        <a
          :href="getLinkoutMgi(smallVariant)"
          class="btn btn-outline-secondary"
          :class="getLinkoutMgi(smallVariant) === '#' ? 'disabled' : ''"
          target="_blank"
          >MGI</a
        >
        <a
          :href="getLinkoutGenCC(smallVariant)"
          class="btn btn-outline-secondary"
          :class="getLinkoutGenCC(smallVariant) === '#' ? 'disabled' : ''"
          target="_blank"
          >GenCC</a
        >
        <a
          :href="getLinkoutMissense3D(smallVariant)"
          class="btn btn-outline-secondary"
          :class="getLinkoutMissense3D(smallVariant) === '#' ? 'disabled' : ''"
          target="_blank"
          >Missense3D</a
        >
        <a
          :href="getLinkoutPubMedPheno(smallVariant, queryStore.queryHpoTerms)"
          class="btn btn-outline-secondary"
          :class="
            getLinkoutPubMedPheno(smallVariant, queryStore.queryHpoTerms) ===
            '#'
              ? 'disabled'
              : ''
          "
          target="_blank"
          >PubMed+Pheno</a
        >
      </div>
    </div>
  </div>
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
