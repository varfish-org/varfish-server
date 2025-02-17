<script setup lang="ts">
/** Display summary read statistics for all samples in a table.
 */
import { computed } from 'vue'

import { type SampleReadStats } from '@/cases_qc/api/types'
import SimpleCard from '@/varfish/components/SimpleCard.vue'

export interface Props {
  sampleNames: string[]
  readStats?: SampleReadStats[]
}
const props = defineProps<Props>()

/** Per-sample (read details) statistics to display in this card */
interface SampleStats {
  readLengthN50: number[]
  totalReads: number[]
  totalYield: number[]
  fragmentFirst: number[] | null
  fragmentLast: number[] | null
}

/** Row-wise read sample statistics, samples ordreed as in `sampleNames.value` */
const sampleStats = computed<SampleStats>(() => {
  const theNames = props.sampleNames
  const result: SampleStats = {
    readLengthN50: new Array<number>(theNames.length).fill(0),
    totalReads: new Array<number>(theNames.length).fill(0),
    totalYield: new Array<number>(theNames.length).fill(0),
    fragmentFirst: new Array<number>(theNames.length).fill(0),
    fragmentLast: new Array<number>(theNames.length).fill(0),
  }

  let anyFragmentFirst = false
  let anyFragmentLast = false
  for (const entry of props.readStats ?? []) {
    const idx = theNames.indexOf(entry.sample)
    result.readLengthN50[idx] = entry.read_length_n50
    result.totalReads[idx] = entry.total_reads
    result.totalYield[idx] = entry.total_yield
    if (entry.fragment_first !== null && result.fragmentFirst !== null) {
      result.fragmentFirst[idx] = entry.fragment_first
      anyFragmentFirst = true
    }
    if (entry.fragment_last !== null && result.fragmentLast !== null) {
      result.fragmentLast[idx] = entry.fragment_last
      anyFragmentLast = true
    }
  }

  if (!anyFragmentFirst) {
    result.fragmentFirst = null
  }
  if (!anyFragmentLast) {
    result.fragmentLast = null
  }

  return result
})

const numberFormatter = Intl.NumberFormat('en', {
  notation: 'compact',
  maximumFractionDigits: 1,
})
</script>

<template>
  <SimpleCard id="readstats" title="Read Statistics" class="col-3 pr-0">
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
            <td class="text-nowrap">read length N50 [bp]</td>
            <td
              v-for="(value, idx) in sampleStats.readLengthN50"
              :key="`n50-${idx}`"
              class="text-right"
            >
              {{ value }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">total reads</td>
            <td
              v-for="(value, idx) in sampleStats.totalReads"
              :key="`total-reads-${idx}`"
              class="text-right"
            >
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">total yield [bp]</td>
            <td
              v-for="(value, idx) in sampleStats.totalYield"
              :key="`yield-${idx}`"
              class="text-right"
            >
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr v-if="sampleStats.fragmentFirst !== null">
            <td class="text-nowrap">read1</td>
            <td
              v-for="(value, idx) in sampleStats.fragmentFirst"
              :key="`read1-${idx}`"
              class="text-right"
            >
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr v-if="sampleStats.fragmentLast !== null">
            <td class="text-nowrap">read2</td>
            <td
              v-for="(value, idx) in sampleStats.fragmentLast"
              :key="`read2-${idx}`"
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
