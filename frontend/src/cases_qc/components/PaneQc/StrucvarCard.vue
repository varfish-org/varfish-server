<script setup lang="ts">
/** Display summary squence variant statistics for all samples in a table.
 */
import { computed } from 'vue'

import { type SampleStrucvarStats } from '@/cases_qc/api/types'
import SimpleCard from '@/varfish/components/SimpleCard.vue'

export interface Props {
  sampleNames: string[]
  strucvarStats?: SampleStrucvarStats[]
}
const props = defineProps<Props>()

/** Per-sample (variant details) statistics to display in this card */
interface SampleStats {
  deletionCount: number[]
  duplicationCount: number[]
  insertionCount: number[]
  inversionCount: number[]
  breakendCount: number[]
}

/** Row-wise read sample statistics, samples ordreed as in `sampleNames.value` */
const sampleStats = computed<SampleStats>(() => {
  const theNames = props.sampleNames
  const result: SampleStats = {
    deletionCount: new Array<number>(theNames.length).fill(0),
    duplicationCount: new Array<number>(theNames.length).fill(0),
    insertionCount: new Array<number>(theNames.length).fill(0),
    inversionCount: new Array<number>(theNames.length).fill(0),
    breakendCount: new Array<number>(theNames.length).fill(0),
  }

  for (const entry of props.strucvarStats ?? []) {
    const idx = theNames.indexOf(entry.sample)
    result.deletionCount[idx] = entry.deletion_count
    result.duplicationCount[idx] = entry.duplication_count
    result.insertionCount[idx] = entry.insertion_count
    result.inversionCount[idx] = entry.inversion_count
    result.breakendCount[idx] = entry.breakend_count
  }

  return result
})

const numberFormatter = Intl.NumberFormat('en', {
  notation: 'compact',
  maximumFractionDigits: 1,
})
</script>

<template>
  <SimpleCard id="readstats" title="StrucVar Statistics" class="col-3 pr-0">
    <div class="table-responsive">
      <table class="table table-sm table-hover mb-0">
        <thead>
          <tr>
            <th>Metric</th>
            <th
              v-for="name in sampleNames"
              :key="`metric-${name}`"
              class="text-left"
            >
              {{ name }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="text-nowrap">DEL</td>
            <td
              v-for="(value, idx) in sampleStats.deletionCount"
              :key="`del-${idx}`"
              class="text-right"
            >
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">DUP</td>
            <td
              v-for="(value, idx) in sampleStats.duplicationCount"
              :key="`dup-${idx}`"
              class="text-right"
            >
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">INS</td>
            <td
              v-for="(value, idx) in sampleStats.insertionCount"
              :key="`ins-${idx}`"
              class="text-right"
            >
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">INV</td>
            <td
              v-for="(value, idx) in sampleStats.inversionCount"
              :key="`inv-${idx}`"
              class="text-right"
            >
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">BND</td>
            <td
              v-for="(value, idx) in sampleStats.breakendCount"
              :key="`bnd-${idx}`"
              class="text-right"
            >
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </SimpleCard>
</template>
