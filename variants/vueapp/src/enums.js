function enumToText(enu) {
  let reversed = {};
  for (const [_, data] of Object.entries(enu)) {
    reversed[data.value] = data.text;
  }
  return reversed;
}

export const QueryStates = Object.freeze({
  Initial: {
    value: 0,
    text: "Initial",
  },
  Running: {
    value: 1,
    text: "Running",
  },
  Finished: {
    value: 2,
    text: "Finished",
  },
  Fetching: {
    value: 3,
    text: "Loading results",
  },
  Fetched: {
    value: 4,
    text: "Results loaded",
  },
  Cancelled: {
    value: 5,
    text: "Cancelled job",
  },
  Error: {
    value: 6,
    text: "Error",
  },
});

export const QueryStateToText = enumToText(QueryStates);

export const DisplayDetails = Object.freeze({
  Coordinates: {
    value: 0,
    text: "Coordinates",
  },
  Clinvar: {
    value: 1,
    text: "ClinVar Summary",
  },
});

export const DisplayFrequencies = Object.freeze({
  Exac: {
    value: 0,
    text: "ExAC",
  },
  ThousandGenomes: {
    value: 1,
    text: "1000 genomes",
  },
  GnomadExomes: {
    value: 2,
    text: "gnomAD exomes",
  },
  GnomadGenomes: {
    value: 3,
    text: "gnomAD genomes",
  },
  InhouseDb: {
    value: 4,
    text: "in-house DB",
  },
  MtDb: {
    value: 5,
    text: "mtDB",
  },
  HelixMtDb: {
    value: 6,
    text: "HelixMTdb",
  },
  Mitomap: {
    value: 7,
    text: "MITOMAP",
  },
});

export const DisplayConstraints = Object.freeze({
  ExacPli: {
    value: 0,
    text: "ExAC pLI",
  },
  ExacZSyn: {
    value: 1,
    text: "ExAC Z syn",
  },
  ExacZMis: {
    value: 2,
    text: "ExAC Z mis",
  },
  GnomadLoeuf: {
    value: 3,
    text: "gnomAD LOEUF",
  },
  GnomadPli: {
    value: 4,
    text: "gnomAD pLI",
  },
  GnomadZSyn: {
    value: 5,
    text: "gnomAD Z syn",
  },
  GnomadZMis: {
    value: 6,
    text: "gnomAD Z mis",
  },
});

export const DisplayColumns = Object.freeze({
  Effect: {
    value: 0,
    text: "Effect",
  },
  EffectText: {
    value: 1,
    text: "Effect Text",
  },
  EffectProtein: {
    value: 2,
    text: "Effect Protein",
  },
  EffectCdna: {
    value: 3,
    text: "Effect cDNA",
  },
  DistanceSplicesite: {
    value: 4,
    text: "Distance to SpliceSite",
  },
});

export const VariantValidatorStates = Object.freeze({
  Initial: 0,
  Running: 1,
  Done: 2,
});

export const EditCommentModes = Object.freeze({
  Off: 0,
  Edit: 1,
  Delete: 2,
});
