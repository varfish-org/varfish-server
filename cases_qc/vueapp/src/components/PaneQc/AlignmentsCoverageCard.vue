<script setup lang="ts">
/** Display per-region coverage card from alignment stats
 */
import { type SampleAlignmentStats } from '@cases_qc/api/types'
import SimpleCard from '@varfish/components/SimpleCard.vue'
import { computed, ref, watch } from 'vue'

export interface Props {
  sampleNames: string[]
  alignmentStats?: SampleAlignmentStats[]
}
const props = defineProps<Props>()

/** Per-sample (read details) statistics to display in this card */
interface SampleStats {
  regionName: string
  meanRd: number[]
  minRdFraction: { [key: number]: number[] }
}

/** The available regions */
const regionNames = computed<string[]>(() => {
  const result = new Set<string>()
  for (const alignmentStats of props.alignmentStats ?? []) {
    for (const regionCoverageStats of alignmentStats.region_coverage_stats) {
      result.add(regionCoverageStats.region_name)
    }
  }
  return Array.from(result).sort()
})

/** The currently selected region name */
const selectedRegionName = ref(regionNames.value[0] ?? '')

/** Initialize the region name when the list changes */
watch(
  () => props.alignmentStats,
  () => {
    selectedRegionName.value = regionNames.value[0] ?? ''
  },
)

/** Keys of coverages from `props.alignmentStats` in ascending order */
const covKeys = computed<number[]>(() => {
  const result = new Set<number>()
  for (const alignmentStats of props.alignmentStats ?? []) {
    for (const regionCoverageStats of alignmentStats.region_coverage_stats) {
      for (const [key, _] of regionCoverageStats.min_rd_fraction) {
        result.add(key)
      }
    }
  }
  return Array.from(result).sort((a, b) => a - b)
})

/** Row-wise read sample statistics, samples ordreed as in `sampleNames.value` */
const regionStats = computed<SampleStats[]>(() => {
  const theNames = props.sampleNames

  const regionToIdx: { [key: string]: number } = {}
  const result: SampleStats[] = []

  for (const alignmentStats of props.alignmentStats ?? []) {
    for (const regionCoverageStats of alignmentStats.region_coverage_stats) {
      let regionSampleStats: SampleStats
      if (regionCoverageStats.region_name in regionToIdx) {
        regionSampleStats = result[regionToIdx[regionCoverageStats.region_name]]
      } else {
        regionToIdx[regionCoverageStats.region_name] = result.length
        result.push({
          regionName: regionCoverageStats.region_name,
          meanRd: new Array<number>(theNames.length).fill(0),
          minRdFraction: {},
        })
        regionSampleStats = result[result.length - 1]
        for (const key of covKeys.value) {
          regionSampleStats.minRdFraction[key] = new Array<number>(
            theNames.length,
          ).fill(0)
        }
      }

      const nameIdx = theNames.indexOf(alignmentStats.sample)
      regionSampleStats.meanRd[nameIdx] = regionCoverageStats.mean_rd
      for (const [key, value] of regionCoverageStats.min_rd_fraction) {
        regionSampleStats.minRdFraction[key][nameIdx] = value
      }
    }
  }

  return result
})

const numberFormatter = Intl.NumberFormat('en', {
  notation: 'compact',
  maximumFractionDigits: 1,
})
</script>

<template>
  <SimpleCard id="alignmentstats-coverage">
    <template #header>
      <div class="form-inline">
        Alignment Stats (Coverage)

        <select
          class="custom-select custom-select-sm ml-auto"
          v-model="selectedRegionName"
          v-if="regionNames?.length"
        >
          <option v-for="regionName of regionNames">
            {{ regionName }}
          </option>
        </select>
      </div>
    </template>

    <template v-for="sampleStats of regionStats">
      <div v-if="sampleStats.regionName === selectedRegionName">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead>
              <tr>
                <th>Sample</th>
                <th>mean cov.</th>
                <th v-for="cov of covKeys" class="text-right text-nowrap">
                  &geq; {{ cov }}x
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(name, nameIdx) of sampleNames">
                <td class="text-nowrap">
                  {{ name }}
                </td>
                <td>{{ sampleStats.meanRd[nameIdx] }}</td>
                <td
                  v-for="value of sampleStats.minRdFraction"
                  class="text-right"
                >
                  {{ value[nameIdx] }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
    <div
      class="text-muted text-center font-italic pt-2 pb-2"
      v-if="!regionStats?.length"
    >
      No coverage data available.
    </div>
  </SimpleCard>
</template>
