import { GenotypeChoice } from './types'

export const GENOTYPE_LABELS: Record<GenotypeChoice, string> = {
  [GenotypeChoice.DE_NOVO]: 'de novo',
  [GenotypeChoice.DOMINANT]: 'dominant',
  [GenotypeChoice.HOMOZYGOUS_RECESSIVE]: 'homozygous recessive',
  [GenotypeChoice.COMPOUND_RECESSIVE]: 'compound recessive',
  [GenotypeChoice.RECESSIVE]: 'recessive',
  [GenotypeChoice.X_RECESSIVE]: 'x recessive',
  [GenotypeChoice.AFFECTED_CARRIERS]: 'affected carriers',
  [GenotypeChoice.ANY]: 'any mode',
}
