<script setup>
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { displayName, formatLargeInt } from '@/varfish/helpers'
import { State } from '@/varfish/storeUtils'

const caseDetailsStore = useCaseDetailsStore()

const tsTv = (member) => {
  // istanbul ignore else
  if (
    caseDetailsStore.caseVariantStats &&
    member.name in caseDetailsStore.caseVariantStats &&
    caseDetailsStore.caseVariantStats[member.name].ontarget_transversions
  ) {
    const stats = caseDetailsStore.caseVariantStats[member.name]
    return (stats.ontarget_transitions / stats.ontarget_transversions).toFixed(
      2,
    )
  } else {
    return 0
  }
}
</script>

<template>
  <div class="card mb-3 varfish-case-list-card flex-grow-1">
    <h5 class="card-header p-2 pl-2">
      <i-mdi-chart-box />
      Variant Quality Control
    </h5>
    <table class="table table-striped table-hover">
      <thead>
        <tr>
          <th>Sample</th>
          <th class="text-center">Ts</th>
          <th class="text-center">Tv</th>
          <th class="text-center">Ts/Tv</th>
          <th class="text-center">X hom./het.</th>
        </tr>
      </thead>
      <tbody>
        <template v-if="caseDetailsStore.storeState.state === State.Active">
          <template
            v-for="member of caseDetailsStore.caseObj.pedigree"
            :key="`member-${member.name}`"
          >
            <tr v-if="member.name in caseDetailsStore.caseVariantStats">
              <td class="font-weight-bold">
                {{ displayName(member.name) }}
              </td>
              <td class="text-right">
                {{
                  formatLargeInt(
                    caseDetailsStore.caseVariantStats[member.name]
                      .ontarget_transitions,
                  )
                }}
              </td>
              <td class="text-right">
                {{
                  formatLargeInt(
                    caseDetailsStore.caseVariantStats[member.name]
                      .ontarget_transversions,
                  )
                }}
              </td>
              <td
                v-if="
                  tsTv(member) <
                    caseDetailsStore.projectSettings.ts_tv_valid_lower ||
                  tsTv(member) >
                    caseDetailsStore.projectSettings.ts_tv_valid_upper
                "
                class="text-right text-danger font-weight-bold"
                :title="`Ts/Tv ratio should be within ${caseDetailsStore.projectSettings.ts_tv_warning_lower}-${caseDetailsStore.projectSettings.ts_tv_warning_upper} but is ${tsTv(
                  member,
                )}`"
              >
                <i-bi-exclamation-circle />
                {{ tsTv(member) }}
              </td>
              <td v-else class="text-right">
                {{ tsTv(member) }}
              </td>
              <td class="text-right">
                {{
                  caseDetailsStore.caseVariantStats[
                    member.name
                  ].chrx_het_hom.toFixed(2)
                }}
              </td>
            </tr>
            <tr v-else>
              <td class="font-weight-bold">{{ displayName(member.name) }}</td>
              <td colspan="4" class="text-muted text-center font-italic">
                No variant stats for sample.
              </td>
            </tr>
          </template>
        </template>
        <tr v-else>
          <td colspan="5" class="text-muted text-center font-italic">
            No variant QC info provided.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
