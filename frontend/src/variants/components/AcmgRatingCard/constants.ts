import { AcmgRating } from '@/variants/api/variantClient'

import { Category, Criterion } from './types'

/** Labels for `Category`. */
export const CATEGORY_LABELS: { [key in Category]: string } = {
  pathogenic_very_strong: 'Very Strong',
  pathogenic_strong: 'Strong',
  pathogenic_moderate: 'Moderate',
  pathogenic_supporting: 'Supporting',
  benign_standalone: 'Standalone',
  benign_very_strong: 'Very Strong',
  benign_strong: 'Strong',
  benign_moderate: 'Moderate',
  benign_supporting: 'Supporting',
}

/** ACMG criteria supporting variant being pathogenic. */
export const CRITERIA_PATHOGENIC: Criterion[] = [
  {
    category: Category.PATHOGENIC_VERY_STRONG,
    name: 'pvs1',
    title: 'PVS1',
    synopsis: 'null variant',
    description:
      'Null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon, single or multi-exon deletion) in a gene where LOF is a known mechanism of disease',
  },
  {
    category: Category.PATHOGENIC_STRONG,
    name: 'ps1',
    title: 'PS1',
    synopsis: 'literature: this AA exchange',
    description:
      'Same amino acid change as a previously established pathogenic variant regardless of nucleotide change',
  },
  {
    category: Category.PATHOGENIC_STRONG,
    name: 'ps2',
    title: 'PS2',
    synopsis: 'confirmed de novo',
    description:
      'De novo (both maternity and paternity confirmed) in a patient with the disease and no family history',
  },
  {
    category: Category.PATHOGENIC_STRONG,
    name: 'ps3',
    title: 'PS3',
    synopsis: 'supported by functional studies',
    description:
      'Well-established in vitro or in vivo functional studies supportive of a damaging effect on the gene or gene product',
  },
  {
    category: Category.PATHOGENIC_STRONG,
    name: 'ps4',
    title: 'PS4',
    synopsis: 'prevalence in disease > controls',
    description:
      'The prevalence of the variant in affected individuals is significantly increased compared with the prevalence in controls',
  },
  {
    category: Category.PATHOGENIC_MODERATE,
    name: 'pm1',
    title: 'PM1',
    synopsis: 'variant in hotspot (missense)',
    description:
      'Located in a mutational hot spot and/or critical and well-established functional domain (e.g., active site of an enzyme) without benign variation',
  },
  {
    category: Category.PATHOGENIC_MODERATE,
    name: 'pm2',
    title: 'PM2',
    synopsis: 'rare; < 1:20.000 in ExAC',
    description:
      'Absent from controls (or at extremely low frequency if recessive) in Exome Sequencing Project, 1000 Genomes Project, or Exome Aggregation Consortium',
  },
  {
    category: Category.PATHOGENIC_MODERATE,
    name: 'pm3',
    title: 'PM3',
    synopsis: 'AR: trans with known pathogenic',
    description:
      'For recessive disorders, detected in trans with a pathogenic variant',
  },
  {
    category: Category.PATHOGENIC_MODERATE,
    name: 'pm4',
    title: 'PM4',
    synopsis: 'protein length change',
    description:
      'Protein length changes as a result of in-frame deletions/insertions in a nonrepeat region or stop-loss variants',
  },
  {
    category: Category.PATHOGENIC_MODERATE,
    name: 'pm5',
    title: 'PM5',
    synopsis: 'literature: AA exchange same pos',
    description:
      'Novel missense change at an amino acid residue where a different missense change determined to be pathogenic has been seen before',
  },
  {
    category: Category.PATHOGENIC_MODERATE,
    name: 'pm6',
    title: 'PM6',
    synopsis: 'assumed de novo',
    description:
      'Assumed de novo, but without confirmation of paternity and maternity',
  },
  {
    category: Category.PATHOGENIC_SUPPORTING,
    name: 'pp1',
    title: 'PP1',
    synopsis: 'cosegregates in family',
    description:
      'Cosegregation with disease in multiple affected family members in a gene definitively known to cause the disease',
  },
  {
    category: Category.PATHOGENIC_SUPPORTING,
    name: 'pp2',
    title: 'PP2',
    synopsis: 'few missense in gene',
    description:
      'Missense variant in a gene that has a low rate of benign missense variation and in which missense variants are a common mechanism of disease',
  },
  {
    category: Category.PATHOGENIC_SUPPORTING,
    name: 'pp3',
    title: 'PP3',
    synopsis: 'predicted pathogenic ≥ 2',
    description:
      'Multiple lines of computational evidence support a deleterious effect on the gene or gene product (conservation, evolutionary, splicing impact, etc.)',
  },
  {
    category: Category.PATHOGENIC_SUPPORTING,
    name: 'pp4',
    title: 'PP4',
    synopsis: 'phenotype/pedigree match gene',
    description:
      "Patient's phenotype or family history is highly specific for a disease with a single genetic etiology",
  },
  {
    category: Category.PATHOGENIC_SUPPORTING,
    name: 'pp5',
    title: 'PP5',
    synopsis: 'reliable source: pathogenic',
    description:
      'Reputable source recently reports variant as pathogenic, but the evidence is not available to the laboratory to perform an independent evaluation',
  },
]

/** ACMG criteria supporting variant being benign. */
export const CRITERIA_BENIGN: Criterion[] = [
  {
    category: Category.BENIGN_STANDALONE,
    name: 'ba1',
    title: 'BA1',
    synopsis: 'allele frequency > 5%',
    description:
      'Allele frequency is >5% in Exome Sequencing Project, 1000 Genomes Project, or Exome Aggregation Consortium',
  },
  {
    category: Category.BENIGN_STRONG,
    name: 'bs1',
    title: 'BS1',
    synopsis: 'disease: allele freq. too high',
    description: 'Allele frequency is greater than expected for disorder',
  },
  {
    category: Category.BENIGN_STRONG,
    name: 'bs2',
    title: 'BS2',
    synopsis: 'observed in healthy individual',
    description:
      'Observed in a healthy adult individual for a recessive (homozygous), dominant (heterozygous), or X-linked (hemizygous) disorder, with full penetrance expected at an early age',
  },
  {
    category: Category.BENIGN_STRONG,
    name: 'bs3',
    title: 'BS3',
    synopsis: 'functional studies: benign',
    description:
      'Well-established in vitro or in vivo functional studies show no damaging effect on protein function or splicing',
  },
  {
    category: Category.BENIGN_STRONG,
    name: 'bs4',
    title: 'BS4',
    synopsis: 'lack of segregation',
    description: 'Lack of segregation in affected members of a family',
  },
  {
    category: Category.BENIGN_SUPPORTING,
    name: 'bp1',
    title: 'BP1',
    synopsis: 'missense in truncation gene',
    description:
      'Missense variant in a gene for which primarily truncating variants are known to cause disease',
  },
  {
    category: Category.BENIGN_SUPPORTING,
    name: 'bp2',
    title: 'BP2',
    synopsis: 'other variant is causative',
    description:
      'Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed in cis with a pathogenic variant in any inheritance pattern',
  },
  {
    category: Category.BENIGN_SUPPORTING,
    name: 'bp3',
    title: 'BP3',
    synopsis: 'in-frame indel in repeat',
    description:
      'In-frame deletions/insertions in a repetitive region without a known function',
  },
  {
    category: Category.BENIGN_SUPPORTING,
    name: 'bp4',
    title: 'BP4',
    synopsis: 'prediction: benign',
    description:
      'Multiple lines of computational evidence suggest no impact on gene or gene product (conservation, evolutionary, splicing impact, etc.)',
  },
  {
    category: Category.BENIGN_SUPPORTING,
    name: 'bp5',
    title: 'BP5',
    synopsis: 'different gene in other case',
    description:
      'Variant found in a case with an alternate molecular basis for disease',
  },
  {
    category: Category.BENIGN_SUPPORTING,
    name: 'bp6',
    title: 'BP6',
    synopsis: 'reputable source: benign',
    description:
      'Reputable source recently reports variant as benign, but the evidence is not available to the laboratory to perform an independent evaluation',
  },
  {
    category: Category.BENIGN_SUPPORTING,
    name: 'bp7',
    title: 'BP7',
    synopsis: 'silent, no splicing/conservation',
    description:
      'A synonymous (silent) variant for which splicing prediction algorithms predict no impact to the splice consensus sequence nor the creation of a new splice site AND the nucleotide is not highly conserved',
  },
]

/** Empty ACMG rating data. */
/** Template for an empty ACMG rating. */
export const EMPTY_ACMG_RATING_TEMPLATE: AcmgRating = {
  pvs1: 0,
  ps1: 0,
  ps2: 0,
  ps3: 0,
  ps4: 0,
  pm1: 0,
  pm2: 0,
  pm3: 0,
  pm4: 0,
  pm5: 0,
  pm6: 0,
  pp1: 0,
  pp2: 0,
  pp3: 0,
  pp4: 0,
  pp5: 0,
  ba1: 0,
  bs1: 0,
  bs2: 0,
  bs3: 0,
  bs4: 0,
  bp1: 0,
  bp2: 0,
  bp3: 0,
  bp4: 0,
  bp5: 0,
  bp6: 0,
  bp7: 0,
  genomeBuild: 'grch37',
  chrom: '',
  pos: 0,
  del: '',
  ins: '',
  userRepr: '',
}
