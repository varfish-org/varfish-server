<script setup>
const props = defineProps({
  effectDetails: Object,
})

const _effectLevels = Object.freeze({
  coding_transcript_intron_variant: 1,
  complex_substitution: 3,
  direct_tandem_duplication: 1,
  disruptive_inframe_deletion: 2,
  disruptive_inframe_insertion: 2,
  downstream_gene_variant: 1,
  feature_truncation: 3,
  '5_prime_UTR_exon_variant': 1,
  '5_prime_UTR_intron_variant': 1,
  frameshift_elongation: 3,
  frameshift_truncation: 3,
  frameshift_variant: 3,
  inframe_deletion: 2,
  inframe_insertion: 2,
  intergenic_variant: 1,
  internal_feature_elongation: 3,
  missense_variant: 2,
  mnv: 3,
  non_coding_transcript_exon_variant: 1,
  non_coding_transcript_intron_variant: 1,
  splice_acceptor_variant: 3,
  splice_donor_variant: 3,
  splice_region_variant: 2,
  start_lost: 3,
  stop_gained: 3,
  stop_lost: 3,
  stop_retained_variant: 1,
  structural_variant: 1,
  synonymous_variant: 1,
  '3_prime_UTR_exon_variant': 1,
  '3_prime_UTR_intron_variant': 1,
  transcript_ablation: 3,
  upstream_gene_variant: 1,
})

const colorVariantEffect = (effect) => {
  if (_effectLevels[effect] === 3) {
    return 'badge-danger'
  } else if (_effectLevels[effect] === 2) {
    return 'badge-warning'
  } else {
    return 'badge-secondary'
  }
}
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h4 class="card-title pb-2">Transcript Information</h4>
    </div>
    <table
      v-if="props.effectDetails"
      class="card-body p-0 table sodar-card-table table-striped table-sm"
    >
      <thead>
        <tr>
          <th class="border-top-0" style="width: 10%">Transcript</th>
          <th class="border-top-0" style="width: 20%">Effects</th>
          <th class="border-top-0" style="width: 35%">HGVS (nuc)</th>
          <th class="border-top-0" style="width: 35%">HGVS (prot)</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(entry, index) in props.effectDetails" :key="index">
          <td>
            {{ entry.transcriptId }}
          </td>
          <td>
            <span
              v-for="(effect, index2) in entry.variantEffects"
              :key="index2"
              class="badge"
              :class="colorVariantEffect(effect)"
              >{{ effect }}</span
            >
          </td>
          <td>
            {{ entry.hgvsNucleotides }}
          </td>
          <td>
            {{ entry.hgvsProtein }}
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="card-body">
      <p class="text-muted text-center">
        Prediction of effect on all overlapping transcript not enabled.
      </p>
    </div>
  </div>
</template>
