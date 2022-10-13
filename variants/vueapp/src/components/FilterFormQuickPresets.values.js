export const quickPresets = Object.freeze({
  defaults: 'defaults',
  de_novo: 'de novo',
  dominant: 'dominant',
  homozygous_recessive: 'homozygous recessive',
  compound_recessive: 'compound recessive',
  recessive: 'recessive',
  x_recessive: 'X-linked recessive',
  clinvar_pathogenic: 'ClinVar pathogenic',
  mitochondrial: 'mitochondrial',
  whole_exome: 'whole exome',
  custom: 'custom',
})

export const presetsInheritance = Object.freeze({
  any: 'any (default)',
  dominant: 'dominant',
  homozygous_recessive: 'homozygous recessive',
  compound_heterozygous: 'compound heterozygous',
  recessive: 'recessive',
  x_recessive: 'X recessive',
  mitochondrial: 'mitochondrial',
  affected_carriers: 'affected carriers',
  custom: 'custom',
})

export const presetsFrequency = Object.freeze({
  any: 'any',
  dominant_super_strict: 'dominant super strict',
  dominant_strict: 'dominant strict (default)',
  dominant_relaxed: 'dominant relaxed',
  recessive_strict: 'recessive strict',
  recessive_relaxed: 'recessive relaxed',
  custom: 'custom',
})

export const presetsImpact = Object.freeze({
  null_variant: 'null variant',
  aa_change_splicing: 'AA change & splicing (default)',
  all_coding_deep_intronic: 'all coding & deep intronic',
  whole_transcript: 'whole transcript',
  any: 'any impact',
  custom: 'custom',
})

export const presetsQuality = Object.freeze({
  super_strict: 'super strict',
  strict: 'strict (default)',
  relaxed: 'relaxed',
  any: 'any',
  custom: 'custom',
})

export const presetsChromosomes = Object.freeze({
  whole_genome: 'whole genome (default)',
  autosomes: 'autosomes',
  x_chromosome: 'X chromosome',
  y_chromosome: 'Y chromosome',
  mt_chromosome: 'MT chromosome',
  custom: 'custom',
})

export const presetsFlags = Object.freeze({
  defaults: 'defaults',
  clinvar_only: 'ClinVar only',
  user_flagged: 'User Flagged',
  custom: 'custom',
})
