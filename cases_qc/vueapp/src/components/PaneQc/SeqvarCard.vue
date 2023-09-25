<script setup lang="ts">
/** Display summary squence variant statistics for all samples in a table.
 */
import { type SampleSeqvarStats } from '@cases_qc/api/types'
import SimpleCard from '@varfish/components/SimpleCard.vue'
import { computed } from 'vue'

export interface Props {
  sampleNames: string[]
  seqvarStats?: SampleSeqvarStats[]
}
const props = defineProps<Props>()

/** Per-sample (variant details) statistics to display in this card */
interface SampleStats {
  snvCount: number[]
  indelCount: number[]
  multiallelicCount: number[]
  transitionCount: number[]
  transversionCount: number[]
  tsvtvRatio: number[]
}

/** Row-wise read sample statistics, samples ordreed as in `sampleNames.value` */
const sampleStats = computed<SampleStats>(() => {
  const theNames = props.sampleNames
  const result: SampleStats = {
    snvCount: new Array<number>(theNames.length).fill(0),
    indelCount: new Array<number>(theNames.length).fill(0),
    multiallelicCount: new Array<number>(theNames.length).fill(0),
    transitionCount: new Array<number>(theNames.length).fill(0),
    transversionCount: new Array<number>(theNames.length).fill(0),
    tsvtvRatio: new Array<number>(theNames.length).fill(0),
  }

  for (const entry of props.seqvarStats ?? []) {
    const idx = theNames.indexOf(entry.sample)
    result.snvCount[idx] = entry.genome_wide.snv_count
    result.indelCount[idx] = entry.genome_wide.indel_count
    result.multiallelicCount[idx] = entry.genome_wide.multiallelic_count
    result.transitionCount[idx] = entry.genome_wide.transition_count
    result.transversionCount[idx] = entry.genome_wide.transversion_count
    result.tsvtvRatio[idx] = entry.genome_wide.tstv_ratio
  }

  return result
})

const numberFormatter = Intl.NumberFormat('en', {
  notation: 'compact',
  maximumFractionDigits: 1,
})
</script>

<template>
  <SimpleCard id="readstats" title="SeqVar Statistics">
    <div class="table-responsive">
      <table class="table table-sm table-hover mb-0">
        <thead>
          <tr>
            <th>Metric</th>
            <th v-for="name in sampleNames" class="text-left">
              {{ name }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="text-nowrap">SNVs</td>
            <td v-for="value in sampleStats.snvCount" class="text-right">
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">InDels</td>
            <td v-for="value in sampleStats.indelCount" class="text-right">
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">multiallelic</td>
            <td
              v-for="value in sampleStats.multiallelicCount"
              class="text-right"
            >
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">transitions</td>
            <td v-for="value in sampleStats.transitionCount" class="text-right">
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">transversions</td>
            <td
              v-for="value in sampleStats.transversionCount"
              class="text-right"
            >
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
          <tr>
            <td class="text-nowrap">transitions</td>
            <td v-for="value in sampleStats.tsvtvRatio" class="text-right">
              {{ numberFormatter.format(value) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </SimpleCard>
</template>
