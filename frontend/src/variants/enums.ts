function enumToText(enu: any) {
  const reversed: { [key in string]: string } = {}
  for (const data of Object.values(enu)) {
    // @ts-ignore
    reversed[data.value] = data.text
  }
  return reversed
}

export const QueryStates = Object.freeze({
  None: {
    value: 'none',
    text: 'None',
  },
  Initial: {
    value: 'initial',
    text: 'Initial',
  },
  Running: {
    value: 'running',
    text: 'Running',
  },
  Timeout: {
    value: 'timeout',
    text: 'Timeout',
  },
  Resuming: {
    value: 'resuming',
    text: 'Resuming',
  },
  Finished: {
    value: 'finished',
    text: 'Finished',
  },
  Fetching: {
    value: 'loading-results',
    text: 'Loading results',
  },
  Fetched: {
    value: 'results-loaded',
    text: 'Results loaded',
  },
  Cancelled: {
    value: 'job-cancelled',
    text: 'Cancelled job',
  },
  Error: {
    value: 'error',
    text: 'Error',
  },
})

export const QueryStateToText = enumToText(QueryStates)

export const ResultStates = Object.freeze({
  None: {
    value: 'none',
    text: 'None',
  },
  Initial: {
    value: 'initial',
    text: 'Initial',
  },
  Fetching: {
    value: 'loading-results',
    text: 'Loading results',
  },
  Fetched: {
    value: 'results-loaded',
    text: 'Results loaded',
  },
  Timeout: {
    value: 'timeout',
    text: 'Timeout',
  },
  Error: {
    value: 'error',
    text: 'Error',
  },
})

export const apiQueryStateToQueryState = (apiQueryState: string) => {
  if (apiQueryState === 'initial') {
    return QueryStates.Initial.value
  } else if (apiQueryState === 'running') {
    return QueryStates.Running.value
  } else if (apiQueryState === 'timeout') {
    return QueryStates.Timeout.value
  } else if (
    apiQueryState === 'done' ||
    apiQueryState === 'complete' /*XXXREMOVEXXX*/
  ) {
    return QueryStates.Finished.value
  } else {
    return QueryStates.Error.value
  }
}

export const DisplayDetails = Object.freeze({
  Coordinates: {
    value: 0,
    text: 'Coordinates',
  },
  Clinvar: {
    value: 1,
    text: 'ClinVar Summary',
  },
})

export const DisplayFrequencies = Object.freeze({
  Exac: {
    value: 0,
    text: 'ExAC',
  },
  ThousandGenomes: {
    value: 1,
    text: '1000 genomes',
  },
  GnomadExomes: {
    value: 2,
    text: 'gnomAD exomes',
  },
  GnomadGenomes: {
    value: 3,
    text: 'gnomAD genomes',
  },
  InhouseDb: {
    value: 4,
    text: 'in-house DB',
  },
  MtDb: {
    value: 5,
    text: 'mtDB',
  },
  HelixMtDb: {
    value: 6,
    text: 'HelixMTdb',
  },
  Mitomap: {
    value: 7,
    text: 'MITOMAP',
  },
})

export const DisplayConstraints = Object.freeze({
  GnomadLoeuf: {
    value: 3,
    text: 'gnomAD LOEUF',
  },
  GnomadPli: {
    value: 4,
    text: 'gnomAD pLI',
  },
  GnomadZSyn: {
    value: 5,
    text: 'gnomAD Z syn',
  },
  GnomadZMis: {
    value: 6,
    text: 'gnomAD Z mis',
  },
})

export const DisplayConstraintsToText = enumToText(DisplayConstraints)

export const DisplayColumns = Object.freeze({
  Effect: {
    value: 'effect_summary',
    text: 'Effect',
  },
  EffectText: {
    value: 'effect',
    text: 'Effect Text',
  },
  EffectProtein: {
    value: 'hgvs_p',
    text: 'Effect Protein',
  },
  EffectCdna: {
    value: 'hgvs_c',
    text: 'Effect cDNA',
  },
  DistanceSplicesite: {
    value: 'exon_dist',
    text: 'Distance to SpliceSite',
  },
})

export const DisplayColumnsToText = enumToText(DisplayColumns)

export enum VariantValidatorStates {
  Initial = 0,
  Running = 1,
  Done = 2,
}
