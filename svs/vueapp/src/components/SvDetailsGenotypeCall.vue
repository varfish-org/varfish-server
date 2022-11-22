<script setup>
import { computed } from 'vue'

import { displayName } from '@varfish/helpers.js'

const props = defineProps({
  currentSvRecord: Object,
})

const GT_FIELDS = Object.freeze({
  quality: 'genotype quality',
  genotype: 'genotype call',
  paired_end_cov: 'total read pairs',
  paired_end_var: 'variant read pairs',
  split_read_cov: 'total split-reads',
  split_read_var: 'variant split reads',
  point_count: 'number of bins/targets',
  average_normalized_cov: 'average normalized coverage',
  average_mapping_quality: 'average mapping quality',
})

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
    <div class="card-header">
      <h4 class="card-title">Genotype and Call Infos</h4>
    </div>
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
          <th>{{ GT_FIELDS[key] ?? key }}</th>
          <td v-for="genotype in currentSvRecord.payload.call_info">
            {{ genotype[key] }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
