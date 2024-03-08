<script setup lang="ts">
import { computed } from 'vue'

import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import { State } from '@varfish/storeUtils'
import { displayName, formatLargeInt } from '@varfish/helpers'

// Store-related.

const caseDetailsStore = useCaseDetailsStore()

// Constant definitions.

const coverages = [0, 10, 20, 30, 40, 50]

// Component state.

const bamStats = computed((): any | null => {
  if (!caseDetailsStore.caseAlignmentStats?.bam_stats) {
    return null
  } else {
    return caseDetailsStore.caseAlignmentStats?.bam_stats
  }
})

// Function definitions.

const getMinCovTarget = (memberName: string, coverage: number): string => {
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
</script>

<template>
  <div class="card mb-3 varfish-case-list-card flex-grow-1">
    <h5 class="card-header p-2 pl-2">
      <i-mdi-chart-box-outline />
      Alignment Quality Control
    </h5>
    <table class="table table-striped table-hover">
      <thead>
        <tr>
          <th style="border-bottom: 0" class="text-center" colspan="3"></th>
          <th style="border-bottom: 0" class="text-center" colspan="1">
            Mean Target
          </th>

          <th
            style="border-bottom: 0"
            class="text-center"
            :colspan="coverages.length"
          >
            Exons covered at least
          </th>
        </tr>
        <tr>
          <th style="width: 15%" class="text-center">Sample</th>
          <th style="width: 15%" class="text-center">Pairs</th>
          <th style="width: 15%" class="text-center">Duplicates</th>
          <th style="width: 15%" class="text-center">Coverage</th>
          <th
            v-for="coverage of coverages"
            :key="`coverage-thead-${coverage}`"
            style="width: 0"
            class="text-nowrap text-center"
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
            :key="`member-${member.name}`"
          >
            <template v-if="member.name in bamStats">
              <th>{{ displayName(member.name) }}</th>
              <td class="text-right">
                {{
                  formatLargeInt(bamStats[member.name].bamstats.sequences / 2)
                }}
              </td>
              <td class="text-right">
                {{
                  (
                    (100.0 *
                      bamStats[member.name].bamstats['reads duplicated']) /
                    bamStats[member.name].bamstats['sequences']
                  ).toFixed(1)
                }}%
              </td>
              <td class="text-right">
                <template
                  v-if="
                    bamStats[member.name].summary &&
                    bamStats[member.name].summary['mean coverage']
                  "
                >
                  {{ bamStats[member.name].summary['mean coverage'] }}x
                </template>
                <template v-else> - </template>
              </td>
              <td
                v-for="coverage in coverages"
                :key="`coverage-tbody-${coverage}`"
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
</template>
