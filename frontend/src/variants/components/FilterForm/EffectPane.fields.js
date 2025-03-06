export const variantTypesFields = Object.freeze([
  { id: 'var_type_snv', label: 'SNV' },
  { id: 'var_type_indel', label: 'indel' },
  { id: 'var_type_mnv', label: 'MNV' },
])

export const transcriptTypeFields = Object.freeze([
  { id: 'transcripts_coding', label: 'coding' },
  { id: 'transcripts_noncoding', label: 'non-coding' },
])

export const effectGroupsFields = Object.freeze([
  { id: 'all', label: 'all' },
  { id: 'nonsynonymous', label: 'nonsynonymous' },
  { id: 'splicing', label: 'splicing' },
  { id: 'coding', label: 'coding' },
  { id: 'utr_intronic', label: 'UTR / intronic' },
  { id: 'noncoding', label: 'non-coding' },
  { id: 'nonsense', label: 'nonsense' },
])

export const detailedEffectGroups = Object.freeze([
  {
    title: 'Coding',
    fields: [
      {
        id: 'disruptive_inframe_deletion',
        label: 'disruptive in-frame deletion',
        so: 'SO:0001826',
        explanation:
          'An inframe decrease in cds length that deletes bases from the coding ' +
          'sequence starting within an existing codon.',
      },
      {
        id: 'disruptive_inframe_insertion',
        label: 'disruptive in-frame insertion',
        so: 'SO:0001824',
        explanation:
          'An inframe increase in cds length that inserts one or more codons into the coding sequence within an existing codon.',
      },
      {
        id: 'feature_elongation',
        label: 'feature elongation',
        so: 'SO:0001907',
        explanation:
          'A sequence variant that causes the extension of a genomic feature, with regard to the reference sequence.',
      },
      {
        id: 'feature_truncation',
        label: 'feature truncation',
        so: 'SO:0001906',
        explanation:
          'A sequence variant that causes the reduction of a genomic feature, with regard to the reference sequence.',
      },
      {
        id: 'frameshift_elongation',
        label: 'frameshift elongation',
        so: 'SO:0001909',
        explanation:
          'A frameshift variant that causes the translational reading frame to be extended relative to the reference feature.',
      },
      {
        id: 'frameshift_truncation',
        label: 'frameshift truncation',
        so: 'SO:0001910',
        explanation:
          'A frameshift variant that causes the translational reading frame to be shortened relative to the reference feature.',
      },
      {
        id: 'frameshift_variant',
        label: 'frameshift variant',
        so: 'SO:0001589',
        explanation:
          'A sequence variant which causes a disruption of the translational reading frame, because the number of nucleotides inserted or deleted is not a multiple of three.',
      },
      {
        id: 'inframe_deletion',
        label: 'inframe deletion',
        so: 'SO:0001822',
        explanation:
          'An inframe non synonymous variant that deletes bases from the coding sequence.',
      },
      {
        id: 'inframe_insertion',
        label: 'inframe insertion',
        so: 'SO:0001821',
        explanation:
          'An inframe non synonymous variant that inserts bases into in the coding sequence.',
      },
      {
        id: 'internal_feature_elongation',
        label: 'internal elongation',
        so: 'SO:0001908',
        explanation:
          'A sequence variant that causes the extension of a genomic feature from within the feature rather than from the terminus of the feature, with regard to the reference sequence.',
      },
      {
        id: 'missense_variant',
        label: 'missense',
        so: 'SO:0001583',
        explanation:
          'A sequence variant, that changes one or more bases, resulting in a different amino acid sequence but where the length is preserved.',
      },
      {
        id: 'mnv',
        label: 'MNV',
        so: 'SO:0002007',
        explanation:
          'An MNV is a multiple nucleotide variant (substitution) in which the inserted sequence is the same length as the replaced sequence.',
      },
      {
        id: 'start_lost',
        label: 'start lost',
        so: 'SO:0002012',
        explanation:
          'A codon variant that changes at least one base of the canonical start codon.',
      },
      {
        id: 'stop_gained',
        label: 'stop gained',
        so: 'SO:0001587',
        explanation:
          'A sequence variant whereby at least one base of a codon is changed, resulting in a premature stop codon, leading to a shortened transcript.',
      },
      {
        id: 'stop_retained_variant',
        label: 'stop retained',
        so: 'SO:0001567',
        explanation:
          'A sequence variant where at least one base in the terminator codon is changed, but the terminator remains.',
      },
      {
        id: 'stop_lost',
        label: 'stop lost',
        so: 'SO:0001578',
        explanation:
          'A sequence variant where at least one base of the terminator codon (stop) is changed, resulting in an elongated transcript.',
      },
      {
        id: 'synonymous_variant',
        label: 'synonymous',
        so: 'SO:0001819',
        explanation:
          'A sequence variant where there is no resulting change to the encoded amino acid.',
      },
      {
        id: 'direct_tandem_duplication',
        label: 'tandem duplication',
        so: 'SO:1000039',
        explanation:
          'A tandem duplication where the individual regions are in the same orientation.',
      },
      {
        id: 'coding_sequence_variant',
        label: 'coding variant',
        so: 'SO:0001580',
        explanation: 'A sequence variant that changes the coding sequence.',
      },
      {
        id: 'conservative_inframe_insertion',
        label: 'conservative in-frame insertion',
        so: 'SO:0001823',
        explanation:
          'An inframe increase in cds length that inserts bases into the coding sequence without changing the amino acid sequence.',
      },
      {
        id: 'conservative_inframe_deletion',
        label: 'conservative in-frame deletion',
        so: 'SO:0001825',
        explanation:
          'An inframe decrease in cds length that deletes bases from the coding sequence without changing the amino acid sequence.',
      },
      {
        id: 'start_retained_variant',
        label: 'start retained',
        so: 'SO:0002019',
        explanation:
          'A sequence variant where at least one base in the start codon is changed, but the start remains.',
      },
      {
        id: 'transcript_amplification',
        label: 'transcript amplification',
        so: 'SO:0001889',
        explanation:
          'A feature amplification of a region containing a transcript.',
      },
      {
        id: 'rare_amino_acid_variant',
        label: 'rare amino acid variant',
        so: 'SO:0002008',
        explanation:
          'A rare amino acid variant is a missense variant that changes an amino acid to one that is rarely used in the human proteome.',
      },
      {
        id: 'protein_altering_variant',
        label: 'protein altering variant',
        so: 'SO:0001818',
        explanation:
          'A sequence variant which is predicted to change the protein encoded in the sequence.',
      },
    ],
  },
  {
    title: 'Off-Exome',
    fields: [
      {
        id: 'downstream_gene_variant',
        label: 'downstream',
        so: 'SO:0001632',
        explanation: "A sequence variant located 3' of a gene.",
      },
      {
        id: 'coding_transcript_intron_variant',
        label: 'intronic (coding transcript)',
        so: 'SO:0001969',
        explanation:
          'A transcript variant occurring within an intron of a coding transcript.',
      },
      {
        id: 'intergenic_variant',
        label: 'intergenic',
        so: 'SO:0001628',
        explanation:
          'A sequence variant located in the intergenic region, between genes.',
      },
      {
        id: 'upstream_gene_variant',
        label: 'upstream',
        so: 'SO:0001631',
        explanation: "A sequence variant located 5' of a gene.",
      },
      {
        id: 'exon_loss_variant',
        label: 'exon loss',
        so: 'SO:0001572',
        explanation:
          'A sequence variant whereby an exon is lost from the transcript.',
      },
      {
        id: 'intron_variant',
        label: 'intron variant',
        so: 'SO:0001627',
        explanation: 'A transcript variant occurring within an intron.',
      },
    ],
  },
  {
    title: 'Non-Coding',
    fields: [
      {
        id: '3_prime_UTR_exon_variant',
        label: "3' UTR exonic",
        so: 'SO:0002089',
        explanation: "An exon UTR variant of the 3' UTR.",
      },
      {
        id: '3_prime_UTR_intron_variant',
        label: "3' UTR intronic",
        so: 'SO:0002090',
        explanation: "An intron UTR variant between 3' UTRs.",
      },
      {
        id: '5_prime_UTR_exon_variant',
        label: "5' UTR exonic",
        so: 'SO:0002092',
        explanation: "An exon UTR variant of the 5' UTR.",
      },
      {
        id: '5_prime_UTR_intron_variant',
        label: "5' UTR intronic",
        so: 'SO:0002091',
        explanation: "An intron UTR variant between 5' UTRs.",
      },
      {
        id: 'non_coding_transcript_exon_variant',
        label: 'n.c. exonic',
        so: 'SO:0001792',
        explanation:
          'A sequence variant that changes non-coding exon sequence in a non-coding transcript.',
      },
      {
        id: 'non_coding_transcript_intron_variant',
        label: 'n.c. intronic',
        so: 'SO:0001970',
        explanation:
          'A transcript variant occurring within an intron of a non coding transcript.',
      },
    ],
  },
  {
    title: 'Splicing',
    fields: [
      {
        id: 'splice_acceptor_variant',
        label: 'splice acceptor',
        so: 'SO:0001574',
        explanation:
          "A splice variant that changes the 2 base region at the 3' end of an intron.",
      },
      {
        id: 'splice_donor_variant',
        label: 'splice donor',
        so: 'SO:0001575',
        explanation:
          "A splice variant that changes the 2 base pair region at the 5' end of an intron.",
      },
      {
        id: 'splice_region_variant',
        label: 'splice region',
        so: 'SO:0001568',
        explanation:
          'A sequence variant in which a change has occurred within the region of the splice site, either within 1-3 bases of the exon or 3-8 bases of the intron.',
      },
      {
        id: 'splice_donor_5th_base_variant',
        label: 'splice donor 5th base',
        so: 'SO:0001787',
        explanation:
          "A splice variant that changes the 5th base of the 5 base pair region at the 5' end of an intron.",
      },
      {
        id: 'splice_donor_region_variant',
        label: 'splice donor region',
        so: 'SO:0001789',
        explanation:
          "A sequence variant that changes the 5 base pair region at the 5' end of an intron.",
      },
      {
        id: 'splice_polypyrimidine_tract_variant',
        label: 'splice polypyrimidine tract',
        so: 'SO:0001624',
        explanation:
          'A variant that changes the polypyrimidine tract of a splice site.',
      },
    ],
  },
  {
    title: 'Structural',
    fields: [
      {
        id: 'structural_variant',
        label: 'structural',
        so: 'SO:0001537',
        explanation:
          'A sequence variant that changes one or more sequence features.',
      },
      {
        id: 'transcript_ablation',
        label: 'transcript ablation',
        so: 'SO:0001893',
        explanation:
          'A feature ablation whereby the deleted region includes a transcript feature.',
      },
    ],
  },
  {
    title: 'Extra Annotations',
    fields: [
      {
        id: 'complex_substitution',
        label: 'complex substitution',
        so: 'SO:1000005',
        explanation:
          'Extra annotation for variants where multiple events can explain variant.',
      },
    ],
  },
])

const _effectGroups = {
  all: [],
  nonsynonymous: [
    'complex_substitution',
    'direct_tandem_duplication',
    'disruptive_inframe_deletion',
    'disruptive_inframe_insertion',
    'exon_loss_variant',
    'feature_elongation',
    'feature_truncation',
    'frameshift_elongation',
    'frameshift_truncation',
    'frameshift_variant',
    'inframe_deletion',
    'inframe_insertion',
    'internal_feature_elongation',
    'missense_variant',
    'mnv',
    'start_lost',
    'stop_gained',
    'stop_lost',
    'structural_variant',
    'transcript_ablation',
    'coding_sequence_variant',
    'conservative_inframe_insertion',
    'conservative_inframe_deletion',
    'transcript_amplification',
    'protein_altering_variant',
  ],
  splicing: [
    'splice_acceptor_variant',
    'splice_donor_variant',
    'splice_region_variant',
    'splice_donor_5th_base_variant',
    'splice_donor_region_variant',
    'splice_polypyrimidine_tract_variant',
  ],
  coding: [
    'stop_retained_variant',
    'synonymous_variant',
    'coding_sequence_variant',
    'conservative_inframe_insertion',
    'conservative_inframe_deletion',
    'start_retained_variant',
    'rare_amino_acid_variant',
    'protein_altering_variant',
  ],
  utr_intronic: [
    'coding_transcript_intron_variant',
    '5_prime_UTR_exon_variant',
    '5_prime_UTR_intron_variant',
    '3_prime_UTR_exon_variant',
    '3_prime_UTR_intron_variant',
    'intron_variant',
  ],
  noncoding: [
    'downstream_gene_variant',
    'intergenic_variant',
    'non_coding_transcript_exon_variant',
    'non_coding_transcript_intron_variant',
    'upstream_gene_variant',
  ],
  nonsense: [
    'frameshift_elongation',
    'frameshift_truncation',
    'frameshift_variant',
    'start_lost',
    'stop_gained',
    'stop_lost',
    'splice_donor_5th_base_variant',
    'splice_donor_region_variant',
    'splice_acceptor_variant',
    'splice_donor_variant',
  ],
}

_effectGroups.all = _effectGroups.nonsynonymous
  .concat(_effectGroups.splicing)
  .concat(_effectGroups.coding)
  .concat(_effectGroups.utr_intronic)
  .concat(_effectGroups.noncoding)
  .concat(_effectGroups.nonsense)

export const effectGroups = Object.freeze(_effectGroups)
