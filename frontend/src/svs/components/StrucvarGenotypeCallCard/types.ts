/** Information about a genotype call for one sample. */
export type CallInfo = { [key: string]: string | string[] }

/** Result row payload. */
export interface Payload {
  call_info: { [key: string]: CallInfo }
}

/** Result row, as needed for the StrucvarGenotypeCallCard. */
export interface ResultRow {
  payload: Payload
}

/** Type for genotype field description. */
export interface GenotypeFieldDescription {
  name: string
  label?: string
  fmt?: (values: string | string[]) => string
}
