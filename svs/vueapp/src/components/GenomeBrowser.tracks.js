const visibilityWindow = 10000000

const hescTadTrack = {
  name: 'hESC TADs',
  sourceType: 'custom',
  visibilityWindow,
  source: {
    url: `/svs/worker/tads/grch37/hesc/?padding=1&chromosome=$CHR&begin=$START&end=$END`,
    method: 'GET',
    contentType: 'application/json',
    mappings: {
      chr: 'chromosome',
      start: 'begin',
    },
    queryable: true,
  },
  format: 'annotation',
  color: 'gray',
}

const curatedMmsTrack = {
  name: 'Curated MMS',
  sourceType: 'custom',
  visibilityWindow,
  source: {
    url: `/svs/worker/pathogenic/grch37/?chromosome=$CHR&begin=$START&end=$END`,
    method: 'GET',
    contentType: 'application/json',
    mappings: {
      chr: 'chromosome',
      start: 'begin',
    },
    queryable: true,
  },
  format: 'annotation',
  color: 'red',
}

const clinvarTrack = {
  name: 'ClinVar SVs',
  sourceType: 'custom',
  visibilityWindow,
  height: 300,
  displayMode: 'SQUISHED',
  source: {
    url: `/svs/worker/clinvar/grch37/?min_pathogenicity=likely-pathogenic&chromosome=$CHR&begin=$START&end=$END`,
    method: 'GET',
    contentType: 'application/json',
    mappings: {
      chr: 'chromosome',
      start: 'begin',
    },
    queryable: true,
  },
  format: 'annotation',
  colorBy: 'pathogenicity',
  colorTable: {
    pathogenic: 'red',
    'likely-pathogenic': 'orange',
    uncertain: 'blue',
    'likely-benign': 'gray',
    benign: 'light gray',
  },
}

const duplicationTrack = {
  name: 'UCSC Segmental Duplications',
  sourceType: 'annotation',
  format: 'bed',
  visibilityWindow,
  url: '/svs/tracks/grch37/ucsc_genomicSuperDups.bed.gz',
  indexURL: '/svs/tracks/grch37/ucsc_genomicSuperDups.bed.gz.tbi',
  color: 'black',
}

const repeatsTrack = {
  name: 'UCSC Repeat Masker',
  sourceType: 'annotation',
  format: 'bed',
  visibilityWindow,
  url: '/svs/tracks/grch37/ucsc_rmsk.bed.gz',
  indexURL: '/svs/tracks/grch37/ucsc_rmsk.bed.gz.tbi',
  color: 'black',
}

const altTrack = {
  name: 'UCSC Alt Loci Track',
  sourceType: 'annotation',
  format: 'bed',
  visibilityWindow,
  url: '/svs/tracks/grch37/ucsc_altSeqLiftOverPsl.bed.gz',
  indexURL: '/svs/tracks/grch37/ucsc_altSeqLiftOverPsl.bed.gz.tbi',
  color: 'black',
}

const fixTrack = {
  name: 'UCSC Fix Track',
  sourceType: 'annotation',
  format: 'bed',
  visibilityWindow,
  url: '/svs/tracks/grch37/ucsc_fixSeqLiftOverPsl.bed.gz',
  indexURL: '/svs/tracks/grch37/ucsc_fixSeqLiftOverPsl.bed.gz.tbi',
  color: 'black',
}

const bgDbTracks = [
  {
    title: 'In-House SVs',
    token: 'inhouse',
  },
  {
    title: 'gnomad-SV',
    token: 'gnomad-sv',
  },
  {
    title: 'DGV SVs',
    token: 'dgv',
  },
  {
    title: 'DGV GS SVs',
    token: 'dgv-gs',
  },
  {
    title: 'ExAC CNVs',
    token: 'exac',
  },
].map(({ title, token }) => {
  return {
    name: title,
    sourceType: 'custom',
    visibilityWindow,
    displayMode: 'SQUISHED',
    source: {
      url: `/svs/worker/bgdb/grch37/${token}/?chromosome=$CHR&begin=$START&end=$END`,
      method: 'GET',
      contentType: 'application/json',
      mappings: {
        chr: 'chromosome',
        start: 'begin',
      },
      queryable: true,
    },
    format: 'annotation',
    color: 'black',
  }
})
export const publicTracks = [
  duplicationTrack,
  repeatsTrack,
  altTrack,
  fixTrack,
  hescTadTrack,
  curatedMmsTrack,
  clinvarTrack,
].concat(bgDbTracks)

export const genCaseTrack = (caseUuid) => ({
  order: -1,
  name: 'Case SVs',
  sourceType: 'custom',
  visibilityWindow,
  source: {
    url: `/svs/ajax/fetch-variants/${caseUuid}/?chromosome=$CHR&start=$START&end=$END`,
    method: 'GET',
    contentType: 'application/json',
    mappings: {
      chr: 'chromosome',
    },
    queryable: true,
  },
  format: 'annotation',
  colorBy: 'sv_type',
  colorTable: {
    DEL: 'red',
    DUP: 'green',
    INV: 'blue',
    '*': 'black',
  },
})
