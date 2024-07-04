export const FREQUENCY_DB_K_SIZES = {
  '1000 Genomes': 1,
  ExAC: 61,
  'gnomAd exomes': 16,
  'gnomAd genomes': 126,
  'in-house DB': null,
  mtDB: 3,
  HelixMTdb: 197,
  MITOMAP: 50,
} satisfies Record<string, number | null>

export type FrequencyDB = keyof typeof FREQUENCY_DB_K_SIZES

export type FrequencyDB_Numbers = {
  freq: number
  het: number
  hom: number
  hemi: number
}

export const FREQUENCY_PRESETS = {
  'dominant super strict': {
    '1000 Genomes': { hom: 0, het: 1, freq: 0.002 },
    ExAC: { hom: 0, het: 1, freq: 0.002 },
    'gnomAd exomes': { hom: 0, het: 1, freq: 0.002 },
    'gnomAd genomes': { hom: 0, het: 1, freq: 0.002 },
    'in-house DB': { freq: 20 },
  },
  'dominant strict': {
    '1000 Genomes': { hom: 0, het: 4, freq: 0.002 },
    ExAC: { hom: 0, het: 10, freq: 0.002 },
    'gnomAd exomes': { hom: 0, het: 20, freq: 0.002 },
    'gnomAd genomes': { hom: 0, het: 4, freq: 0.002 },
    'in-house DB': { freq: 20 },
    mtDB: { freq: 0.01 },
    HelixMTdb: { hom: 200, freq: 0.01 },
  },
  'dominant relaxed': {
    '1000 Genomes': { hom: 0, het: 10, freq: 0.01 },
    ExAC: { hom: 0, het: 25, freq: 0.01 },
    'gnomAd exomes': { hom: 0, het: 50, freq: 0.01 },
    'gnomAd genomes': { hom: 0, het: 20, freq: 0.01 },
    'in-house DB': { freq: 20 },
    mtDB: { hom: 50, freq: 0.15 },
    HelixMTdb: { hom: 400, freq: 0.15 },
  },
  'recessive strict': {
    '1000 Genomes': { hom: 1, het: 24, freq: 0.001 },
    ExAC: { hom: 0, het: 60, freq: 0.001 },
    'gnomAd exomes': { hom: 0, het: 120, freq: 0.001 },
    'gnomAd genomes': { hom: 0, het: 15, freq: 0.001 },
    'in-house DB': { freq: 20 },
  },
  'recessive relaxed': {
    '1000 Genomes': { hom: 4, het: 240, freq: 0.01 },
    ExAC: { hom: 10, het: 600, freq: 0.01 },
    'gnomAd exomes': { hom: 20, het: 1200, freq: 0.01 },
    'gnomAd genomes': { hom: 4, het: 150, freq: 0.01 },
    'in-house DB': { freq: 20 },
  },
  any: {},
} satisfies Record<
  string,
  Partial<Record<FrequencyDB, Partial<FrequencyDB_Numbers>>>
>

export type FrequencyPresetKey = keyof typeof FREQUENCY_PRESETS

export type FrequencyDB_Value = {
  checked: boolean
  numbers: Partial<FrequencyDB_Numbers>
}

export type FrequencyDB_Values = Record<FrequencyDB, FrequencyDB_Value>

export type FrequencyModel = {
  preset: FrequencyPresetKey
  values: FrequencyDB_Values
}
