export interface GenotypeValue {
  gt: string
  dp?: number
  ad?: number
  gq?: number
}

export type Genotype = { [key: string]: GenotypeValue }

export interface Payload {
  genotype: Genotype
}

export interface ResultRow {
  payload: Payload
}
