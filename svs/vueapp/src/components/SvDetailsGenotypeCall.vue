<script setup>
import { computed } from 'vue'

import { displayName } from '@varfish/helpers.js'

const props = defineProps({
  currentSvRecord: Object,
})

const GT_FIELDS = Object.freeze({
  quality: { label: 'genotype quality' },
  genotype: { label: 'genotype call' },
  paired_end_cov: { label: 'total read pairs' },
  paired_end_var: { label: 'variant read pairs' },
  split_read_cov: { label: 'total split-reads' },
  split_read_var: { label: 'variant split reads' },
  point_count: { label: 'number of bins/targets' },
  average_normalized_cov: { label: 'average normalized coverage' },
  average_mapping_quality: { label: 'average mapping quality' },
  matched_gt_criteria: {
    label: 'matched genotype criteria',
    fmt: (arr) => arr.join(', '),
  },
  effective_genotype: { label: 'effective genotype' },
})

const identity = (x) => x

const allKeys = computed(() => {
  if (!props.currentSvRecord?.payload?.call_info) {
    return []
  }

  let tmp = []
  for (let call_info of Object.values(
    props.currentSvRecord.payload.call_info
  )) {
    tmp = tmp.concat(
      Object.entries(call_info)
        .filter(([_, value]) => value !== null)
        .map(([key, _]) => key)
    )
  }
  let result = Array.from(new Set(tmp))
  result.sort()
  return result
})
</script>

<template>
  <div class="card">
    <table class="table table-striped table-hover" v-if="currentSvRecord">
      <thead>
        <tr>
          <th>Sample</th>

          <template v-for="(_, sample) in currentSvRecord.payload.call_info">
            <th>
              {{ displayName(sample) }}
            </th>
          </template>
        </tr>
      </thead>
      <tbody>
        <tr v-for="key in allKeys">
          <th>{{ GT_FIELDS[key]?.label ?? key }}</th>
          <td v-for="genotype in currentSvRecord.payload.call_info">
            {{ (GT_FIELDS[key]?.fmt ?? identity)(genotype[key]) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
