import { SeqvarsVariantConsequenceChoiceList } from '@varfish-org/varfish-api/lib'

/** Helper type to unpack, e.g., `Array<T1 | T2>`. */
export type _Unpacked<T> = T extends (infer U)[] ? U : T

/** Define choices for variant consequences. */
export type SeqvarsVariantConsequenceChoice =
  _Unpacked<SeqvarsVariantConsequenceChoiceList>

/** Enumeration for consequence groups. */
export enum ConsequenceGroup {
  ALL = 'all',
  NONSYNONYMOUS = 'nonsynonymous',
  SPLICING = 'splicing',
  CODING = 'coding',
  UTR_INTRONIC = 'utr_intronic',
  OFF_EXOME = 'off_exome',
  NON_CODING = 'non_coding',
  NONSENSE = 'nonsense',
}

/** One consequence group. */
export interface ConsequenceGroupInfo {
  /** Consequence group label. */
  label: string
  /** Key identifying the consequence group. */
  key: ConsequenceGroup
  /** Values in `data.variant_consequences`. */
  valueKeys: SeqvarsVariantConsequenceChoice[]
}

/** One choice of consequence. */
export interface ConsequenceChoice {
  label: string
  key: SeqvarsVariantConsequenceChoice
}

/** Consequence choices in "coding" category. */
export const CODING_CONSEQUENCES: ConsequenceChoice[] = [
  { label: 'transcript ablation', key: 'transcript_ablation' },
  { label: 'transcript amplification', key: 'transcript_amplification' },
  { label: 'exon loss', key: 'exon_loss_variant' },
  { label: 'frameshift variant', key: 'frameshift_variant' },
  { label: 'start lost', key: 'start_lost' },
  { label: 'stop gained', key: 'stop_gained' },
  { label: 'stop lost', key: 'stop_lost' },
  {
    label: 'disruptive inframe insertion',
    key: 'disruptive_inframe_insertion',
  },
  { label: 'disruptive inframe deletion', key: 'disruptive_inframe_deletion' },
  {
    label: 'conservative inframe insertion',
    key: 'conservative_inframe_insertion',
  },
  {
    label: 'conservative inframe deletion',
    key: 'conservative_inframe_deletion',
  },
  { label: 'in-frame indel', key: 'inframe_indel' },
  { label: 'missense', key: 'missense_variant' },
  { label: 'start retained', key: 'start_retained_variant' },
  { label: 'stop retained', key: 'stop_retained_variant' },
  { label: 'synonymous', key: 'synonymous_variant' },
  { label: 'coding', key: 'coding_sequence_variant' },
] as const

/** Consequence choices in "off-exomes" category. */
export const OFF_EXOMES_CONSEQUENCES: ConsequenceChoice[] = [
  { label: 'upstream', key: 'upstream_gene_variant' },
  { label: 'downstream', key: 'downstream_gene_variant' },
  { label: 'intronic', key: 'intron_variant' },
  { label: 'intergenic', key: 'intergenic_variant' },
] as const

/** Consequence choices in "non-coding" category. */
export const NON_CODING_CONSEQUENCES: ConsequenceChoice[] = [
  { label: "5' UTR exon variant", key: '5_prime_UTR_exon_variant' },
  { label: "5' UTR intron variant", key: '5_prime_UTR_intron_variant' },
  { label: "3' UTR exon variant", key: '3_prime_UTR_exon_variant' },
  { label: "3' UTR intron variant", key: '3_prime_UTR_intron_variant' },
  { label: 'non-coding exonic', key: 'non_coding_transcript_exon_variant' },
  { label: 'non-coding intronic', key: 'non_coding_transcript_intron_variant' },
] as const

/** Consequence choices in "splicing" category. */
export const SPLICING_CONSEQUENCES: ConsequenceChoice[] = [
  { label: 'splice acceptor (-1, -2)', key: 'splice_acceptor_variant' },
  { label: 'splice donor (+1, +2)', key: 'splice_donor_variant' },
  { label: 'splice donor 5th-base', key: 'splice_donor_5th_base_variant' },
  { label: 'splice region (-3, +3, ..., +8)', key: 'splice_region_variant' },
  { label: 'splice donor region', key: 'splice_donor_region_variant' },
  {
    label: 'splice polypyrimidine tract variant',
    key: 'splice_polypyrimidine_tract_variant',
  },
] as const

/** Defined consequence groups. */
export const CONSEQUENCE_GROUP_INFOS: ConsequenceGroupInfo[] = [
  {
    label: 'all',
    key: ConsequenceGroup.ALL,
    valueKeys: CODING_CONSEQUENCES.map((elem) => elem.key)
      .concat(OFF_EXOMES_CONSEQUENCES.map((elem) => elem.key))
      .concat(NON_CODING_CONSEQUENCES.map((elem) => elem.key))
      .concat(SPLICING_CONSEQUENCES.map((elem) => elem.key)),
  },
  {
    label: 'nonsynonymous',
    key: ConsequenceGroup.NONSYNONYMOUS,
    valueKeys: [
      'transcript_ablation',
      'transcript_amplification',
      'exon_loss_variant',
      'frameshift_variant',
      'start_lost',
      'stop_gained',
      'stop_lost',
      'disruptive_inframe_deletion',
      'disruptive_inframe_insertion',
      'conservative_inframe_insertion',
      'conservative_inframe_deletion',
      'missense_variant',
      'coding_sequence_variant',
    ],
  },
  {
    label: 'splicing',
    key: ConsequenceGroup.SPLICING,
    valueKeys: [
      'splice_acceptor_variant',
      'splice_donor_variant',
      'splice_region_variant',
      'splice_donor_5th_base_variant',
      'splice_donor_region_variant',
      'splice_polypyrimidine_tract_variant',
    ],
  },
  {
    label: 'coding',
    key: ConsequenceGroup.CODING,
    valueKeys: [
      'transcript_ablation',
      'transcript_amplification',
      'exon_loss_variant',
      'frameshift_variant',
      'start_lost',
      'stop_gained',
      'stop_lost',
      'disruptive_inframe_deletion',
      'disruptive_inframe_insertion',
      'conservative_inframe_insertion',
      'conservative_inframe_deletion',
      'missense_variant',
      'synonymous_variant',
    ],
  },
  {
    label: 'UTR / intronic',
    key: ConsequenceGroup.UTR_INTRONIC,
    valueKeys: [
      '5_prime_UTR_exon_variant',
      '5_prime_UTR_intron_variant',
      '3_prime_UTR_exon_variant',
      '3_prime_UTR_intron_variant',
    ],
  },
  {
    label: 'off-exome',
    key: ConsequenceGroup.OFF_EXOME,
    valueKeys: [
      'upstream_gene_variant',
      'downstream_gene_variant',
      'intron_variant',
      'intergenic_variant',
    ],
  },
  {
    label: 'non-coding',
    key: ConsequenceGroup.NON_CODING,
    valueKeys: [
      'non_coding_transcript_exon_variant',
      'non_coding_transcript_intron_variant',
    ],
  },
  {
    label: 'nonsense',
    key: ConsequenceGroup.NONSENSE,
    valueKeys: [
      'transcript_ablation',
      'exon_loss_variant',
      'frameshift_variant',
      'splice_acceptor_variant',
      'splice_donor_variant',
      'start_lost',
      'stop_gained',
      'stop_lost',
    ],
  },
] as const

/** Type for the consequence group checkbox state. */
export interface ConsequenceGroupState {
  /** Whether the group is checked. */
  checked: boolean
  /** Whether the group is indeterminate. */
  indeterminate: boolean
}
