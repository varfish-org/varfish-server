<script setup lang="ts">
/** Display summary read statistics for all samples in a table.
 */
import { type SampleAlignmentStats } from '@cases_qc/api/types'
import SimpleCard from '@varfish/components/SimpleCard.vue'
import { computed } from 'vue'

export interface Props {
  sampleNames: string[]
  alignmentStats?: SampleAlignmentStats[]
}
const props = defineProps<Props>()

/** Per-sample (read details) statistics to display in this card */
interface SampleStats {
  mapped: number[]
  duplicates: number[]
  mismatchRate: number[]
  isizeMean: number[]
  isizeStddev: number[]
}

/** Row-wise read sample statistics, samples ordreed as in `sampleNames.value` */
const sampleStats = computed<SampleStats>(() => {
  const theNames = props.sampleNames
  const result: SampleStats = {
    mapped: new Array<number>(theNames.length).fill(0),
    duplicates: new Array<number>(theNames.length).fill(0),
    mismatchRate: new Array<number>(theNames.length).fill(0),
    isizeMean: new Array<number>(theNames.length).fill(0),
    isizeStddev: new Array<number>(theNames.length).fill(0),
  }

  for (const entry of props.alignmentStats ?? []) {
    const idx = theNames.indexOf(entry.sample)
    result.mapped[idx] = entry.detailed_counts.mapped
    result.duplicates[idx] = entry.detailed_counts.duplicates
    result.mismatchRate[idx] = entry.detailed_counts.mismatch_rate
    result.isizeMean[idx] = entry.insert_size_stats.insert_size_mean
    result.isizeStddev[idx] = entry.insert_size_stats.insert_size_stddev
  }

  return result
})

const numberFormatter = Intl.NumberFormat('en', {
  notation: 'compact',
  maximumFractionDigits: 1,
})

const zip = (a, b) => a.map((k, i) => [k, b[i]])
</script>

<template>
  <SimpleCard id="alignmentstats-summary" title="Alignment Stats (Summary)" class="col-3 pr-0">
    <div class="table-responsive">
      <table class="table table-sm table-hover mb-0">
        <thead>
          <tr>
            <th>Metric</th>
            <th v-for="name in sampleNames" class="text-left text-nowrap">
              {{ name }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="text-nowrap">reads mapped</td>
            <td v-for="value in sampleStats.mapped" class="text-right">
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">duplicates</td>
            <td
              v-for="[d, m] in zip(sampleStats.duplicates, sampleStats.mapped)"
              class="text-right"
            >
              <template v-if="m && m > 0">
                {{ numberFormatter.format((d / m) * 100.0) }}%
              </template>
              <template v-else> 0% </template>
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">mismatch rate</td>
            <td v-for="value in sampleStats.mismatchRate" class="text-right">
              {{ numberFormatter.format(value * 100) }}%
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">fragment length mean [bp]</td>
            <td v-for="value in sampleStats.isizeMean" class="text-right">
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">fragment length stddev [bp]</td>
            <td v-for="value in sampleStats.isizeStddev" class="text-right">
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </SimpleCard>
</template>
