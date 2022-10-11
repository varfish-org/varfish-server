<script setup>
const props = defineProps({
  gene: Object,
  smallVariant: Object,
  hgmdProEnabled: Boolean,
  hgmdProPrefix: String,
  umdPredictorApiToken: String,
})

const getGeneSymbol = () => {
  if (props.gene) {
    return props.gene.symbol || props.gene.gene_symbol
  } else {
    return undefined
  }
}

const getLinkoutDgv = () => {
  if (!props.smallVariant) {
    return null
  } else if (props.smallVariant.release === 'GRCh37') {
    return `http://dgv.tcag.ca/gb2/gbrowse/dgv2_hg19/?name=${props.smallVariant.chromosome}:${props.smallVariant.start}-${props.smallVariant.end};search=Search`
  } else if (props.smallVariant.release === 'GRCh38') {
    return `http://dgv.tcag.ca/gb2/gbrowse/dgv2_hg38/?name=${props.smallVariant.chromosome}:${props.smallVariant.start}-${props.smallVariant.end};search=Search`
  } else {
    return null
  }
}

const getLinkoutEnsembl = () => {
  if (!props.smallVariant) {
    return null
  } else if (props.smallVariant.release === 'GRCh37') {
    return `https://grch37.ensembl.org/Homo_sapiens/Location/View?r=${props.smallVariant.chromosome}:${props.smallVariant.start}-${props.smallVariant.end}`
  } else if (props.smallVariant.release === 'GRCh38') {
    return `https://ensembl.org/Homo_sapiens/Location/View?r=${props.smallVariant.chromosome}:${props.smallVariant.start}-${props.smallVariant.end}`
  } else {
    return null
  }
}

const getLinkoutGnomad = () => {
  if (!props.smallVariant) {
    return null
  } else if (props.smallVariant.release === 'GRCh37') {
    return `http://gnomad.broadinstitute.org/region/${props.smallVariant.chromosome}:${props.smallVariant.start}-${props.smallVariant.end}`
  } else if (props.smallVariant.release === 'GRCh38') {
    return `http://gnomad.broadinstitute.org/region/${props.smallVariant.chromosome}:${props.smallVariant.start}-${props.smallVariant.end}`
  } else {
    return null
  }
}

const getLinkoutUmd = (umdToken) => {
  if (!props.smallVariant) {
    return null
  } else if (props.smallVariant.release === 'GRCh37' && umdToken) {
    return `http://umd-predictor.eu/webservice.php?chromosome=chr${props.smallVariant.chromosome}&c_position=${props.smallVariant.start}&wt_nucleotide=${props.smallVariant.reference}&mutant_nucleotide=${props.smallVariant.alternative}&token=${umdToken}`
  } else {
    return null
  }
}

const getLinkoutUcsc = () => {
  if (!props.smallVariant) {
    return null
  } else if (props.smallVariant.release === 'GRCh37') {
    return `https://genome-euro.ucsc.edu/cgi-bin/hgTracks?db=hg19&position=${props.smallVariant.chromosome}:${props.smallVariant.start}-${props.smallVariant.end}`
  } else if (props.smallVariant.release === 'GRCh38') {
    return `https://genome-euro.ucsc.edu/cgi-bin/hgTracks?db=hg38&position=${props.smallVariant.chromosome}:${props.smallVariant.start}-${props.smallVariant.end}`
  } else {
    return null
  }
}

const getLinkoutVarsome = () => {
  if (!props.smallVariant) {
    return null
  } else if (props.smallVariant.release === 'GRCh37') {
    return `https://varsome.com/variant/hg19/chr${props.smallVariant.chromosome}-${props.smallVariant.start}-${props.smallVariant.reference}-${props.smallVariant.alternative}`
  } else if (props.smallVariant.release === 'GRCh38') {
    return `https://varsome.com/variant/hg38/${props.smallVariant.chromosome}-${props.smallVariant.start}-${props.smallVariant.reference}-${props.smallVariant.alternative}`
  } else {
    return null
  }
}

const getLinkoutVariantValidator = () => {
  if (!props.smallVariant) {
    return null
  } else if (props.smallVariant.release === 'GRCh37') {
    return true
  } else if (props.smallVariant.release === 'GRCh38') {
    return true
  } else {
    return null
  }
}

const getLinkoutVarseak = () => {
  if (!props.smallVariant) {
    return null
  } else {
    return `https://varseak.bio/ssp.php?gene=${getGeneSymbol()}&hgvs=${
      props.smallVariant.hgvs_c
    }&transcript=${props.smallVariant.refseq_transcript_id}`
  }
}
</script>

<template>
  <div class="row" v-if="props.gene">
    <div class="col-12 pl-0 pr-0">
      <strong class="text-muted">Gene @</strong>
      <div class="btn-group btn-group-sm pl-2 mb-2">
        <a
          :href="'https://www.omim.org/search/?search=' + getGeneSymbol()"
          class="btn btn-outline-secondary"
          target="_blank"
          >OMIM</a
        >
        <a
          :href="
            'https://www.genecards.org/cgi-bin/carddisp.pl?gene=' +
            getGeneSymbol()
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >GeneCards</a
        >
        <a
          :href="
            props.gene.entrez_id
              ? 'https://www.ncbi.nlm.nih.gov/gene/' + props.gene.entrez_id
              : 'https://www.ncbi.nlm.nih.gov/gene/?term=(' +
                getGeneSymbol() +
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
            getGeneSymbol()
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >HGNC</a
        >
        <a
          :href="'http://www.hgmd.cf.ac.uk/ac/gene.php?gene=' + getGeneSymbol()"
          class="btn btn-outline-secondary"
          target="_blank"
          >HGMD Public</a
        >
        <a
          :href="'https://www.proteinatlas.org/search/' + getGeneSymbol()"
          class="btn btn-outline-secondary"
          target="_blank"
          >ProteinAtlas</a
        >
        <a
          :href="'https://www.ncbi.nlm.nih.gov/pubmed/?term=' + getGeneSymbol()"
          class="btn btn-outline-secondary"
          target="_blank"
          >PubMed</a
        >
        <a
          :href="
            'https://www.ncbi.nlm.nih.gov/clinvar/?term=' + getGeneSymbol()
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >ClinVar</a
        >
        <a
          :href="
            'https://' +
            (smallVariant.release === 'GRCh37' ? 'grch37' : 'www') +
            '.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g=' +
            smallVariant.ensembl_gene_id
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >EnsEMBL</a
        >
        <a
          :href="
            'https://stuart.radboudumc.nl/metadome/dashboard/transcript/' +
            smallVariant.ensembl_transcript_id
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >MetaDome</a
        >
        <a
          :href="
            'https://panelapp.genomicsengland.co.uk/panels/entities/' +
            getGeneSymbol()
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >PanelApp</a
        >
        <a
          v-if="props.hgmdProEnabled"
          :href="props.hgmdProPrefix + '/gene.php?gene=' + getGeneSymbol()"
          class="btn btn-outline-secondary"
          target="_blank"
          >HGMD Pro</a
        >
        <a
          :href="
            'https://gnomad.broadinstitute.org/gene/' +
            smallVariant.ensembl_gene_id
          "
          class="btn btn-outline-secondary"
          target="_blank"
          >gnomAD</a
        >
        <a
          :href="'http://www.informatics.jax.org/marker/' + smallVariant.mgi_id"
          class="btn btn-outline-secondary"
          :class="!smallVariant.mgi_id ? 'disabled' : ''"
          target="_blank"
          >MGI</a
        >
        <a
          :href="'https://search.thegencc.org/genes/' + smallVariant.hgnc_id"
          class="btn btn-outline-secondary"
          :class="!smallVariant.hgnc_id ? 'disabled' : ''"
          target="_blank"
          >GenCC</a
        >
        <a
          :href="
            'http://missense3d.bc.ic.ac.uk:8080/search_direct?uniprot=' +
            smallVariant.uniprot_ids
          "
          class="btn btn-outline-secondary"
          :class="!smallVariant.uniprot_ids ? 'disabled' : ''"
          target="_blank"
          >Missense3D</a
        >
        <a
          :href="
            'http://missense3d.bc.ic.ac.uk:8080/search_direct?uniprot=' +
            smallVariant.uniprot_ids
          "
          class="btn btn-outline-secondary"
          :class="!smallVariant.uniprot_ids ? 'disabled' : ''"
          target="_blank"
          >PubMed</a
        >
      </div>
    </div>
  </div>
  <div class="row" v-if="props.smallVariant">
    <div class="col-12 pl-0 pr-0">
      <strong class="text-muted">Variant @</strong>
      <div class="btn-group btn-group-sm pl-2 mb-2">
        <a
          :href="getLinkoutUcsc()"
          class="btn btn-outline-secondary"
          :class="getLinkoutUcsc ? '' : 'disabled'"
          target="_blank"
          >UCSC</a
        >
        <a
          :href="getLinkoutEnsembl()"
          class="btn btn-outline-secondary"
          :class="getLinkoutEnsembl ? '' : 'disabled'"
          target="_blank"
          >EnsEMSBL</a
        >
        <a
          :href="getLinkoutDgv()"
          class="btn btn-outline-secondary"
          :class="getLinkoutDgv ? '' : 'disabled'"
          target="_blank"
          >DGV</a
        >
        <a
          :href="getLinkoutGnomad()"
          class="btn btn-outline-secondary"
          :class="getLinkoutGnomad ? '' : 'disabled'"
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
          :href="getLinkoutVarseak()"
          class="btn btn-outline-secondary"
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
