<script setup>
import { State } from '@/varfish/storeUtils'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { displayName, formatLargeInt } from '@/varfish/helpers'
import { computed } from 'vue'

const caseDetailsStore = useCaseDetailsStore()

const coverages = [0, 10, 20, 30, 40, 50]

const bamStats = computed(() => {
  if (!caseDetailsStore.caseAlignmentStats?.bam_stats) {
    return null
  } else {
    return caseDetailsStore.caseAlignmentStats?.bam_stats
  }
})

const getMinCovTarget = (memberName, coverage) => {
  if (
    !bamStats.value ||
    !bamStats.value[memberName] ||
    !bamStats.value[memberName].min_cov_target ||
    !bamStats.value[memberName].min_cov_target[coverage]
  ) {
    return '-'
  } else {
    const perc = bamStats.value[memberName].min_cov_target[coverage]
    return `${perc}%`
  }
}

const percentDuplicates = (bamstats) => {
  if (bamstats?.sequences) {
    return (100.0 * bamstats?.['reads duplicated']) / bamstats.sequences
  } else {
    return 0.0
  }
}
</script>

<template>
  <div v-if="bamstats">
    <h6 class="mt-3">Stats</h6>

    <table class="table table-striped table-hover">
      <thead>
        <tr>
          <th style="width: 15%" class="text-center">Sample</th>
          <th style="width: 15%" class="text-right">Pairs</th>
          <th style="width: 15%" class="text-right">Duplicates</th>
          <th style="width: 15%" class="text-right">&#248; Insert Size</th>
          <th style="width: 15%" class="text-right">SD Insert Size</th>
          <th style="width: 15%" class="text-right">Mean Target Coverage</th>
          <th style="width: 15%" class="text-right">Target Size</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="member of caseDetailsStore.caseObj.pedigree"
          :key="`member-summary-${member.name}`"
        >
          <th>{{ displayName(member.name) }}</th>
          <td class="text-right">
            {{ formatLargeInt(bamStats[member.name].bamstats?.sequences / 2) }}
          </td>
          <td class="text-right">
            {{ percentDuplicates(bamStats[member.name].bamstats).toFixed(1) }}%
          </td>
          <td class="text-right">
            {{ bamStats[member.name].bamstats?.['insert size average'] ?? '-' }}
          </td>
          <td class="text-right">
            {{
              bamStats[member.name].bamstats?.[
                'insert size standard deviation'
              ] ?? '-'
            }}
          </td>
          <td
            v-if="bamStats[member.name].summary?.['mean coverage']"
            class="text-right"
          >
            {{ bamStats[member.name].summary['mean coverage'] }}&nbsp;x
          </td>
          <td v-else class="text-right">-</td>
          <td
            v-if="bamStats[member.name].summary?.['total target size']"
            class="text-right"
          >
            {{
              bamStats[member.name].summary?.['total target size'] ?? '-'
            }}&nbsp;x
          </td>
          <td v-else class="text-right">-</td>
        </tr>
      </tbody>
    </table>

    <h6 class="mt-3">Target Coverage</h6>

    <table class="table table-striped table-hover">
      <thead>
        <tr>
          <th style="width: 15%" class="text-center">Sample</th>
          <th
            v-for="coverage of coverages"
            :key="`coverage-${coverage}`"
            style="width: 0"
            class="text-nowrap text-right"
          >
            ≥ {{ coverage }}
          </th>
        </tr>
      </thead>
      <tbody>
        <template
          v-if="caseDetailsStore.storeState.state === State.Active && bamStats"
        >
          <tr
            v-for="member of caseDetailsStore.caseObj.pedigree"
            :key="`member-cov-${member.name}`"
          >
            <template v-if="member.name in bamStats">
              <th>{{ displayName(member.name) }}</th>
              <td
                v-for="coverage in coverages"
                :key="`cov-${coverage}`"
                class="text-right"
              >
                {{ getMinCovTarget(member.name, coverage) }}
              </td>
            </template>
          </tr>
        </template>
        <tr v-else>
          <td
            :colspan="coverages.length + 4"
            class="text-center text-muted font-italic"
          >
            No coverage information provided.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div v-else class="text-muted align-center">
    BAM statistics not available.
  </div>
</template>
