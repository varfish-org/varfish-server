<script setup>
/** Editor component for quality.
 */

import { randomString } from '@varfish/common'

/** Define props. */
const props = defineProps({
  querySettings: Object,
  idSuffix: {
    type: String,
    default: randomString(),
  },
})
</script>

<template>
  <div class="mr-2 mt-2">
    <div class="form-group">
      <label :for="'dp_het' + idSuffix"> Heterozygous Coverage </label>
      <input
        type="text"
        class="form-control"
        placeholder="Minimal het. coverage"
        :id="'dp_het' + idSuffix"
        v-model="querySettings.dp_het"
      />
      <small class="form-text text-muted">
        The minimal coverage at heterozygous sites.
      </small>
    </div>

    <div class="form-group">
      <label :for="'dp_hom' + idSuffix"> Homozygous Coverage </label>
      <input
        type="text"
        class="form-control"
        placeholder="Minimal het. coverage"
        :id="'dp_hom' + idSuffix"
        v-model="querySettings.dp_hom"
      />
      <small class="form-text text-muted">
        The minimal coverage at homozygous sites.
      </small>
    </div>

    <div class="form-group">
      <label :for="'ab' + idSuffix"> Allelic Balance </label>
      <input
        type="text"
        class="form-control"
        placeholder="Minimal allelic balance"
        :id="'ab' + idSuffix"
        v-model="querySettings.ab"
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
        type="text"
        class="form-control"
        placeholder="Minimal genotype coverage"
        :id="'gq' + idSuffix"
        v-model="querySettings.gq"
      />
      <small class="form-text text-muted">
        The minimal phred-scaled genotype quality.
      </small>
    </div>

    <div class="form-group">
      <label :for="'ad' + idSuffix"> Allele Support (min.) </label>
      <input
        type="text"
        class="form-control"
        placeholder="Minimal allele support"
        :id="'ad' + idSuffix"
        v-model="querySettings.ad"
      />
      <small class="form-text text-muted">
        The minimal number of reads to support an allele.
      </small>
    </div>

    <div class="form-group">
      <label :for="'ad_max' + idSuffix"> Allele Support (max.) </label>
      <input
        type="text"
        class="form-control"
        placeholder="Max. allele support"
        :id="'ad_max' + idSuffix"
        v-model="querySettings.ad_max"
      />
      <small class="form-text text-muted">
        The maximal number of reads to support an allele.
      </small>
    </div>

    <div class="form-group">
      <label :for="'fail' + idSuffix"> QC Failure Effect </label>
      <select class="custom-select" v-model="querySettings.fail">
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
</template>
