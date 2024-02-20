import { Section } from './types'

/** Sections in the navigation. */
export const SECTIONS: { [key: string]: Section[] } = {
  GENE: [
    { id: 'gene-overview', title: 'Overview' },
    { id: 'gene-pathogenicity', title: 'Pathogenicity' },
    { id: 'gene-conditions', title: 'Conditions' },
    { id: 'gene-expression', title: 'Expression' },
    { id: 'gene-clinvar', title: 'ClinVar' },
    { id: 'gene-literature', title: 'Literature' },
  ],
  SEQVAR: [
    { id: 'seqvar-csq', title: 'Consequences' },
    { id: 'seqvar-clinvar', title: 'ClinVar' },
    { id: 'seqvar-scores', title: 'Scores' },
    { id: 'seqvar-freqs', title: 'Frequencies' },
    { id: 'seqvar-tools', title: 'Tools' },
    { id: 'seqvar-flags', title: 'Flags' },
    { id: 'seqvar-comments', title: 'Comments' },
    { id: 'seqvar-acmg', title: 'ACMG Rating' },
    { id: 'seqvar-ga4ghbeacons', title: 'GA4GH Beacons' },
    { id: 'seqvar-variantvalidator', title: 'VariantValidator' },
  ],
}
