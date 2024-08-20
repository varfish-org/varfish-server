<script setup>
// eslint-disable

/** Editor component for quality.
 */
import { randomString } from '@/varfish/common'

/** Define props. */
const props = defineProps({
  querySettings: Object,
  idSuffix: {
    type: String,
    default: randomString(),
  },
})
// eslint-enable
</script>

<template>
  <!-- eslint-disable -->
  <div
    class="mr-2 mt-2"
    v-if="props.querySettings !== null && props.querySettings !== undefined"
  >
    <div class="form-group">
      <label :for="'dp_het' + idSuffix"> Heterozygous Coverage </label>
      <input
        :id="'dp_het' + idSuffix"
        v-model="querySettings.dp_het"
        type="text"
        class="form-control"
        placeholder="Minimal het. coverage"
      />
      <small class="form-text text-muted">
        The minimal coverage at heterozygous sites.
      </small>
    </div>

    <div class="form-group">
      <label :for="'dp_hom' + idSuffix"> Homozygous Coverage </label>
      <input
        :id="'dp_hom' + idSuffix"
        v-model="querySettings.dp_hom"
        type="text"
        class="form-control"
        placeholder="Minimal het. coverage"
      />
      <small class="form-text text-muted">
        The minimal coverage at homozygous sites.
      </small>
    </div>

    <div class="form-group">
      <label :for="'ab' + idSuffix"> Allelic Balance </label>
      <input
        :id="'ab' + idSuffix"
        v-model="querySettings.ab"
        type="text"
        class="form-control"
        placeholder="Minimal allelic balance"
      />
      <small class="form-text text-muted">
        The minimal allelic balance (alternative allele coverage divided by
        total coverage or reference coverage divided by total coverage,
        whichever is smaller).
      </small>
    </div>

    <div class="form-group">
      <label :for="'gq' + idSuffix"> Genotype Quality </label>
      <input
        :id="'gq' + idSuffix"
        v-model="querySettings.gq"
        type="text"
        class="form-control"
        placeholder="Minimal genotype coverage"
      />
      <small class="form-text text-muted">
        The minimal phred-scaled genotype quality.
      </small>
    </div>

    <div class="form-group">
      <label :for="'ad' + idSuffix"> Allele Support (min.) </label>
      <input
        :id="'ad' + idSuffix"
        v-model="querySettings.ad"
        type="text"
        class="form-control"
        placeholder="Minimal allele support"
      />
      <small class="form-text text-muted">
        The minimal number of reads to support an allele.
      </small>
    </div>

    <div class="form-group">
      <label :for="'ad_max' + idSuffix"> Allele Support (max.) </label>
      <input
        :id="'ad_max' + idSuffix"
        v-model="querySettings.ad_max"
        type="text"
        class="form-control"
        placeholder="Max. allele support"
      />
      <small class="form-text text-muted">
        The maximal number of reads to support an allele.
      </small>
    </div>

    <div class="form-group">
      <label :for="'fail' + idSuffix"> QC Failure Effect </label>
      <select v-model="querySettings.fail" class="custom-select">
        <option value="drop-variant">drop variant</option>
        <option value="ignore">ignore</option>
        <option value="no-call">no-call</option>
      </select>
      <small class="form-text text-muted">
        The effect that a QC failure of one genotype has (drop whole variant,
        ignore QC failure, interpret failing QC as no/call ("./.").
      </small>
    </div>
  </div>
  <!-- eslint-enable -->
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
