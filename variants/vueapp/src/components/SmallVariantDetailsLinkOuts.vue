<template>
  <div class="row">
    <div class="col-12 pl-0 pr-0">
      <strong class="text-muted">Gene @</strong>
      <div class="btn-group btn-group-sm pl-2 mb-2">
        <a
          :href="
            'https://www.omim.org/search/?search=' + detailsStore.getGeneSymbol
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >OMIM</a
        >
        <a
          :href="
            'https://www.genecards.org/cgi-bin/carddisp.pl?gene=' +
            detailsStore.getGeneSymbol
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >GeneCards</a
        >
        <a
          :href="
            detailsStore.gene.entrez_id
              ? 'https://www.ncbi.nlm.nih.gov/gene/' +
                detailsStore.gene.entrez_id
              : 'https://www.ncbi.nlm.nih.gov/gene/?term=(' +
                detailsStore.getGeneSymbol +
                'AND' +
                '&quot;Homo+sapiens&quot;)'
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >Entrez</a
        >
        <a
          :href="
            'https://www.genenames.org/cgi-bin/gene_symbol_report?match=' +
            detailsStore.getGeneSymbol
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >HGNC</a
        >
        <a
          :href="
            'http://www.hgmd.cf.ac.uk/ac/gene.php?gene=' +
            detailsStore.getGeneSymbol
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >HGMD Public</a
        >
        <a
          :href="
            'https://www.proteinatlas.org/search/' + detailsStore.getGeneSymbol
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >ProteinAtlas</a
        >
        <a
          :href="
            'https://www.ncbi.nlm.nih.gov/pubmed/?term=' +
            detailsStore.getGeneSymbol
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >PubMed</a
        >
        <a
          :href="
            'https://www.ncbi.nlm.nih.gov/clinvar/?term=' +
            detailsStore.getGeneSymbol
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >ClinVar</a
        >
        <a
          :href="
            'https://' +
            (detailsStore.smallVariant.release === 'GRCh37'
              ? 'grch37'
              : 'www') +
            '.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g=' +
            detailsStore.smallVariant.ensembl_gene_id
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >EnsEMBL</a
        >
        <a
          :href="
            'https://stuart.radboudumc.nl/metadome/dashboard/transcript/' +
            detailsStore.smallVariant.ensembl_transcript_id
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >MetaDome</a
        >
        <a
          :href="
            'https://panelapp.genomicsengland.co.uk/panels/entities/' +
            detailsStore.getGeneSymbol
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >PanelApp</a
        >
        <a
          v-if="queryStore.hgmdProEnabled"
          :href="
            queryStore.hgmdProPrefix +
            '/gene.php?gene=' +
            detailsStore.getGeneSymbol
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >HGMD Pro</a
        >
        <a
          :href="
            'https://gnomad.broadinstitute.org/gene/' +
            detailsStore.smallVariant.ensembl_gene_id
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >gnomAD</a
        >
        <a
          :href="
            'http://www.informatics.jax.org/marker/' +
            detailsStore.smallVariant.mgi_id
          "
          class="btn btn-outline-secondary"
          :class="!detailsStore.smallVariant.mgi_id ? 'disabled' : ''"
          target="_blank"
          >MGI</a
        >
        <a
          :href="
            'https://search.thegencc.org/genes/' +
            detailsStore.smallVariant.hgnc_id
          "
          class="btn btn-outline-secondary"
          :class="!detailsStore.smallVariant.hgnc_id ? 'disabled' : ''"
          target="_blank"
          >GenCC</a
        >
        <a
          :href="
            'http://missense3d.bc.ic.ac.uk:8080/search_direct?uniprot=' +
            detailsStore.smallVariant.uniprot_ids
          "
          class="btn btn-outline-secondary"
          :class="!detailsStore.smallVariant.uniprot_ids ? 'disabled' : ''"
          target="_blank"
          >Missense3D</a
        >
        <a
          :href="
            'http://missense3d.bc.ic.ac.uk:8080/search_direct?uniprot=' +
            detailsStore.smallVariant.uniprot_ids
          "
          class="btn btn-outline-secondary"
          :class="!detailsStore.smallVariant.uniprot_ids ? 'disabled' : ''"
          target="_blank"
          >PubMed</a
        >
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-12 pl-0 pr-0">
      <strong class="text-muted">Variant @</strong>
      <div class="btn-group btn-group-sm pl-2 mb-2">
        <a
          :href="detailsStore.getLinkoutUcsc"
          class="btn btn-outline-secondary"
          :class="detailsStore.getLinkoutUcsc ? '' : 'disabled'"
          target="_blank"
          >UCSC</a
        >
        <a
          :href="detailsStore.getLinkoutEnsembl"
          class="btn btn-outline-secondary"
          :class="detailsStore.getLinkoutEnsembl ? '' : 'disabled'"
          target="_blank"
          >EnsEMSBL</a
        >
        <a
          :href="detailsStore.getLinkoutDgv"
          class="btn btn-outline-secondary"
          :class="detailsStore.getLinkoutDgv ? '' : 'disabled'"
          target="_blank"
          >DGV</a
        >
        <a
          :href="detailsStore.getLinkoutGnomad"
          class="btn btn-outline-secondary"
          :class="detailsStore.getLinkoutGnomad ? '' : 'disabled'"
          target="_blank"
          >gnomAD</a
        >
      </div>
      <strong class="text-muted pl-3">Query @</strong>
      <div class="btn-group btn-group-sm pl-2 mb-2">
        <!-- Todo hgmd pro Linkout -->
        <a class="btn btn-outline-secondary disabled" target="_blank"
          >Human Splicing Finder</a
        >
        <a
          :href="detailsStore.getLinkoutVarseak"
          class="btn btn-outline-secondary"
          target="_blank"
          >varSEAK Splicing</a
        >
        <button class="btn btn-sm btn-outline-secondary" :disabled="true">
          PolyPhen2
        </button>
        <a
          :href="detailsStore.getLinkoutUmd(queryStore.umdPredictorApiToken)"
          class="btn btn-outline-secondary"
          :class="queryStore.umdPredictorApiToken ? '' : 'disabled'"
          target="_blank"
          >UMD Predictor</a
        >
      </div>
    </div>
  </div>
</template>

<script>
import { variantDetailsStore } from '@variants/stores/variantDetails'
import { filterQueryStore } from '@variants/stores/filterQuery'

export default {
  components: {},
  setup() {
    const detailsStore = variantDetailsStore()
    const queryStore = filterQueryStore()
    return {
      detailsStore,
      queryStore,
    }
  },
}
</script>
