<script setup>
import { useCaseDetailsStore } from '../stores/case-details'
import { computed } from 'vue'

import CaseDetailsFlagIcon from './CaseDetailFlagIcon.vue'

const caseDetailsStore = useCaseDetailsStore()

const acmgCountByLevel = computed(() => {
  const result = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }
  for (const acmgRating of caseDetailsStore.acmgRatingList) {
    const level = acmgRating.class_override ?? acmgRating.class_auto ?? 3
    result[level] += 1
  }
  return result
})

const flagIds = [
  'flag_bookmarked',
  'flag_candidate',
  'flag_final_causative',
  'flag_for_validation',
  'flag_no_disease_association',
  'flag_segregates',
  'flag_doesnt_segregate',
]

const buildComputedAnnoCountByFlag = (theList) => {
  return computed(() => {
    const result = Object.fromEntries(flagIds.map((flagId) => [flagId, 0]))
    for (const varAnno of caseDetailsStore.varAnnoList) {
      for (const flagId of flagIds) {
        if (varAnno[flagId]) {
          result[flagId] += 1
        }
      }
    }
    return result
  })
}

const varAnnoCountByFlag = buildComputedAnnoCountByFlag(
  caseDetailsStore.varAnnoList,
)

const svAnnoCountByFlag = buildComputedAnnoCountByFlag(
  caseDetailsStore.svrAnnoList,
)
</script>

<template>
  <div class="card mb-3 varfish-case-list-card flex-grow-1">
    <h5 class="card-header p-2 pl-2">
      <i-mdi-bookmark-multiple />
      Flag &amp; Comment Summary
    </h5>
    <ul class="list-group list-group-flush">
      <li class="list-group-item pl-0">
        <div class="row">
          <div class="col-3 text-nowrap">
            <strong> ACMG-Classified Variants </strong>
          </div>
          <div class="col-1 text-right">
            {{ caseDetailsStore.acmgRatingList.length }}
          </div>
          <div class="col-8">
            V:{{ acmgCountByLevel[5] }} &nbsp; IV:{{
              acmgCountByLevel[4]
            }}
            &nbsp; III:{{ acmgCountByLevel[3] }} &nbsp; II:{{
              acmgCountByLevel[2]
            }}
            &nbsp; I:{{ acmgCountByLevel[1] }}
          </div>
        </div>
      </li>
      <li class="list-group-item pl-0">
        <div class="row">
          <div class="col-3 text-nowrap">
            <strong> Flagged Variants </strong>
          </div>
          <div class="col-1 text-right">6</div>
          <div class="col-8">
            <span v-for="flagId in flagIds" class="mr-3">
              <CaseDetailsFlagIcon :flag="flagId" />:{{
                varAnnoCountByFlag[flagId]
              }}
            </span>
          </div>
        </div>
      </li>
      <li class="list-group-item pl-0">
        <div class="row">
          <div class="col-3 text-nowrap">
            <strong> Commented Variants </strong>
          </div>
          <div class="col-1 text-right">
            {{ caseDetailsStore.varCommentList.length }}
          </div>
        </div>
      </li>
      <li class="list-group-item pl-0">
        <div class="row">
          <div class="col-3 text-nowrap">
            <strong> Flagged SVs </strong>
          </div>
          <div class="col-1 text-right">6</div>
          <div class="col-8">
            <span v-for="flagId in flagIds" class="mr-3">
              <CaseDetailsFlagIcon :flag="flagId" />:{{
                svAnnoCountByFlag[flagId]
              }}
            </span>
          </div>
        </div>
      </li>
      <li class="list-group-item pl-0">
        <div class="row">
          <div class="col-3 text-nowrap">
            <strong> Commented SVs </strong>
          </div>
          <div class="col-1 text-right">
            {{ caseDetailsStore.svCommentList.length }}
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>
