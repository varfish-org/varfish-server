export const svSubTypeGroups = Object.freeze([
  {
    title: 'Deletion',
    fields: [
      {
        id: 'DEL',
        label: 'Deletion',
        explanation: 'A deletion of the donor with respect to the reference',
      },
      {
        id: 'DEL:ME',
        label: 'Mobile Element',
        explanation:
          'A deletion of a mobile element in the donor with respect to the reference',
      },
      {
        id: 'DEL:ME:SVA',
        label: 'SVA Deletion',
        explanation:
          'A deletion of an SVA mobile element in the donor with respect to the reference',
      },
      {
        id: 'DEL:ME:L1',
        label: 'L1 Deletion',
        explanation:
          'A deletion of an L1 mobile element in the donor with respect to the reference',
      },
      {
        id: 'DEL:ME:ALU',
        label: 'ALU Deletion',
        explanation:
          'A deletion of an ALU mobile element in the donor with respect to the reference',
      },
    ],
  },
  {
    title: 'Duplication',
    fields: [
      {
        id: 'DUP',
        label: 'Duplication',
        explanation: 'Duplication in the donor with respect to the reference',
      },
      {
        id: 'DUP:TANDEM',
        label: 'Duplication',
        explanation:
          'Tandem duplication in the donor with respect to the reference',
      },
    ],
  },
  {
    title: 'Inversion',
    fields: [
      {
        id: 'INV',
        label: 'Inversion',
        explanation: 'Inversion in the donor with respect to the reference',
      },
    ],
  },
  {
    title: 'Insertion',
    fields: [
      {
        id: 'INS',
        label: 'Insertion',
        explanation:
          'Insertion in the donor with respect to the reference (e.g., ancestral sequence ' +
          'missing in the reference)',
      },
      {
        id: 'INS:ME',
        label: 'Mobile Element Insertion',
        explanation:
          'Mobile element insertion in donor with respect to the reference',
      },
      {
        id: 'INS:ME:SVA',
        label: 'SVA Insertion',
        explanation:
          'SVA mobile element insertion in donor with respect to the reference',
      },
      {
        id: 'INS:ME:L1',
        label: 'L1 Insertion',
        explanation:
          'L1 mobile element insertion in donor with respect to the reference',
      },
      {
        id: 'INS:ME:ALU',
        label: 'ALU Insertion',
        explanation:
          'ALU mobile element insertion in donor with respect to the reference',
      },
    ],
  },
  {
    title: 'Break-Ends',
    fields: [
      {
        id: 'BND',
        label: 'Break-End',
        explanation:
          'Chromosome adjacency in the donor not present in reference',
      },
    ],
  },
  {
    title: 'Copy Number Variation',
    fields: [
      {
        id: 'CNV',
        label: 'Copy Number Variant',
        explanation: 'Copy number variant in the donor',
      },
    ],
  },
])

const _svTypeGroups = {
  _all: [],
  DEL: ['DEL', 'DEL:ME', 'DEL:ME:SVA', 'DEL:ME:L1', 'DEL:ME:ALU'],
  DUP: ['DUP', 'DUP:TANDEM'],
  INV: ['INV'],
  INS: ['INS', 'INS:ME', 'INS:ME:SVA', 'INS:ME:L1', 'INS:ME:ALU'],
  BND: ['BND'],
  CNV: ['CNV'],
}
_svTypeGroups._all = _svTypeGroups.DEL.concat(_svTypeGroups.DUP)
  .concat(_svTypeGroups.INV)
  .concat(_svTypeGroups.INS)
  .concat(_svTypeGroups.BND)
  .concat(_svTypeGroups.CNV)
export const svTypeGroups = Object.freeze(_svTypeGroups)

export const svTypeFields = Object.freeze([
  { id: '_all', label: '_all' },
  { id: 'DEL', label: 'Deletions' },
  { id: 'DUP', label: 'Duplications' },
  { id: 'INV', label: 'Inversions' },
  { id: 'INS', label: 'Insertions' },
  { id: 'BND', label: 'Break-Ends' },
  { id: 'CNV', label: 'CNVs' },
])

export const txEffectFields = Object.freeze([
  {
    id: 'transcript_variant',
    label: 'whole transcript',
    explanation: 'the whole transcript is affected',
  },
  {
    id: 'exon_variant',
    label: 'exonic',
    explanation: 'at least one exon is affected',
  },
  {
    id: 'splice_region_variant',
    label: 'splic region',
    explanation:
      'the first/last 3bp of an exon or first/last 8bp of an intron are affected',
  },
  {
    id: 'intron_variant',
    label: 'intronic',
    explanation: 'an intron is affected',
  },
  {
    id: 'upstream_variant',
    label: 'upstream (5kbp)',
    explanation: 'upstream region of 5kbp is affected',
  },
  {
    id: 'downstream_variant',
    label: 'downstream (5kbp)',
    explanation: 'downstream region of 5kbp is affected',
  },
  {
    id: 'intergenic_variant',
    label: 'include intergenic',
    explanation: 'also include intergenic variants (none of the other impacts)',
  },
])
