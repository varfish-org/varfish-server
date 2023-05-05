import { stopWords } from '@variants/components/VariantDetailsLinkOuts.values.json'

export const getGeneSymbol = (gene) => {
  if (gene) {
    return gene.symbol || gene.gene_symbol
  } else {
    return undefined
  }
}

export const getLinkoutDgv = (smallVariant) => {
  if (!smallVariant) {
    return '#'
  } else if (smallVariant.release === 'GRCh37') {
    return `http://dgv.tcag.ca/gb2/gbrowse/dgv2_hg19/?name=${smallVariant.chromosome}:${smallVariant.start}-${smallVariant.end};search=Search`
  } else if (smallVariant.release === 'GRCh38') {
    return `http://dgv.tcag.ca/gb2/gbrowse/dgv2_hg38/?name=${smallVariant.chromosome}:${smallVariant.start}-${smallVariant.end};search=Search`
  } else {
    return '#'
  }
}

export const getLinkoutEnsembl = (smallVariant) => {
  if (!smallVariant) {
    return '#'
  } else if (smallVariant.release === 'GRCh37') {
    return `https://grch37.ensembl.org/Homo_sapiens/Location/View?r=${smallVariant.chromosome}:${smallVariant.start}-${smallVariant.end}`
  } else if (smallVariant.release === 'GRCh38') {
    return `https://ensembl.org/Homo_sapiens/Location/View?r=${smallVariant.chromosome}:${smallVariant.start}-${smallVariant.end}`
  } else {
    return '#'
  }
}

export const getLinkoutEnsemblGene = (smallVariant) => {
  if (!smallVariant) {
    return '#'
  } else if (smallVariant.release === 'GRCh37') {
    return `https://grch37.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g=${smallVariant.ensembl_gene_id}`
  } else if (smallVariant.release === 'GRCh38') {
    return `https://www.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g=${smallVariant.ensembl_gene_id}`
  } else {
    return '#'
  }
}

export const getLinkoutMetaDome = (smallVariant) => {
  if (!smallVariant) {
    return '#'
  } else {
    return `https://stuart.radboudumc.nl/metadome/dashboard/transcript/${smallVariant.ensembl_transcript_id}`
  }
}

export const getLinkoutGnomadGene = (smallVariant) => {
  if (!smallVariant) {
    return '#'
  } else if (smallVariant.release === 'GRCh37') {
    return `https://gnomad.broadinstitute.org/gene/${smallVariant.ensembl_gene_id}?dataset=gnomad_r2_1`
  } else if (smallVariant.release === 'GRCh38') {
    return `https://gnomad.broadinstitute.org/gene/${smallVariant.ensembl_gene_id}?dataset=gnomad_r3`
  } else {
    return '#'
  }
}

export const getLinkoutMgi = (smallVariant) => {
  if (smallVariant && smallVariant.mgi_id) {
    return `http://www.informatics.jax.org/marker/${smallVariant.mgi_id}`
  } else {
    return '#'
  }
}

export const getLinkoutGenCC = (smallVariant) => {
  if (smallVariant && smallVariant.hgnc_id) {
    return `https://search.thegencc.org/genes/${smallVariant.hgnc_id}`
  } else {
    return '#'
  }
}

export const getLinkoutMissense3D = (smallVariant) => {
  if (smallVariant && smallVariant.uniprot_ids) {
    return `http://missense3d.bc.ic.ac.uk:8080/search_direct?uniprot=${smallVariant.uniprot_ids}`
  } else {
    return '#'
  }
}

export const getLinkoutPubMedPheno = (smallVariant, hpoTerms) => {
  const symbol = getGeneSymbol(smallVariant)
  if (symbol && hpoTerms.length > 0) {
    let terms = []
    for (const [_, text] of Object.entries(hpoTerms)) {
      const tokens = text.toLowerCase().split(/\W+/)
      let words = []
      for (const token of tokens) {
        if (!stopWords.includes(token)) {
          words.push(token)
        }
      }
      terms.push('(' + words.join(' AND ') + ')')
    }
    return `https://www.ncbi.nlm.nih.gov/pubmed/?term=${symbol} AND (${terms.join(
      ' OR '
    )})`
  } else {
    return '#'
  }
}

export const getLinkoutEntrez = (gene) => {
  const symbol = getGeneSymbol(gene)
  if (symbol) {
    if (gene.entrez_id) {
      return `https://www.ncbi.nlm.nih.gov/gene/${gene.entrez_id}`
    } else {
      return `https://www.ncbi.nlm.nih.gov/gene/?term=(${symbol} AND &quot;Homo+sapiens&quot;)`
    }
  } else {
    return '#'
  }
}

export const getLinkoutGnomad = (smallVariant) => {
  if (!smallVariant) {
    return '#'
  } else if (smallVariant.release === 'GRCh37') {
    return `https://gnomad.broadinstitute.org/region/${smallVariant.chromosome}:${smallVariant.start}-${smallVariant.end}?dataset=gnomad_r2_1`
  } else if (smallVariant.release === 'GRCh38') {
    return `https://gnomad.broadinstitute.org/region/${smallVariant.chromosome}:${smallVariant.start}-${smallVariant.end}?dataset=gnomad_r3`
  } else {
    return '#'
  }
}

export const getLinkoutUmd = (umdToken, smallVariant) => {
  if (!smallVariant) {
    return '#'
  } else if (smallVariant.release === 'GRCh37' && umdToken) {
    return `http://umd-predictor.eu/webservice.php?chromosome=chr${smallVariant.chromosome}&c_position=${smallVariant.start}&wt_nucleotide=${smallVariant.reference}&mutant_nucleotide=${smallVariant.alternative}&token=${umdToken}`
  } else {
    return '#'
  }
}

export const getLinkoutUcsc = (smallVariant) => {
  if (!smallVariant) {
    return '#'
  } else if (smallVariant.release === 'GRCh37') {
    return `https://genome-euro.ucsc.edu/cgi-bin/hgTracks?db=hg19&position=${smallVariant.chromosome}:${smallVariant.start}-${smallVariant.end}`
  } else if (smallVariant.release === 'GRCh38') {
    return `https://genome-euro.ucsc.edu/cgi-bin/hgTracks?db=hg38&position=${smallVariant.chromosome}:${smallVariant.start}-${smallVariant.end}`
  } else {
    return '#'
  }
}

export const getLinkoutVarsome = (smallVariant) => {
  if (!smallVariant) {
    return '#'
  } else if (smallVariant.release === 'GRCh37') {
    return `https://varsome.com/variant/hg19/chr${smallVariant.chromosome}-${smallVariant.start}-${smallVariant.reference}-${smallVariant.alternative}`
  } else if (smallVariant.release === 'GRCh38') {
    return `https://varsome.com/variant/hg38/${smallVariant.chromosome}-${smallVariant.start}-${smallVariant.reference}-${smallVariant.alternative}`
  } else {
    return '#'
  }
}

export const getLinkoutVariantValidator = (smallVariant) => {
  if (!smallVariant) {
    return '#'
  } else if (smallVariant.release === 'GRCh37') {
    return 'https://notimplemented'
  } else if (smallVariant.release === 'GRCh38') {
    return 'https://notimplemented'
  } else {
    return '#'
  }
}

export const getLinkoutVarseak = (smallVariant, gene) => {
  if (!smallVariant || !gene) {
    return '#'
  } else {
    return `https://varseak.bio/ssp.php?gene=${getGeneSymbol(gene)}&hgvs=${
      smallVariant.hgvs_c
    }&transcript=${smallVariant.refseq_transcript_id}`
  }
}

export const getLinkoutMt85 = (smallVariant) => {
  if (!smallVariant) {
    return '#'
  } else if (smallVariant.release === 'GRCh37') {
    return `https://www.genecascade.org/MT85/ChrPos85.cgi?chromosome=${smallVariant.chromosome}&position=${smallVariant.start}&ref=${smallVariant.reference}&alt=${smallVariant.alternative}`
  } else {
    return '#'
  }
}

export const getLinkoutMt2021 = (smallVariant) => {
  if (!smallVariant) {
    return '#'
  } else if (smallVariant.release === 'GRCh37') {
    return `https://www.genecascade.org/MTc2021/ChrPos102.cgi?chromosome=${smallVariant.chromosome}&position=${smallVariant.start}&ref=${smallVariant.reference}&alt=${smallVariant.alternative}`
  } else {
    return '#'
  }
}
