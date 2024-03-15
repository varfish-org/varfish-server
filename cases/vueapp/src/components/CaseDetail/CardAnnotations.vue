<script setup lang="ts">
import { useVariantFlagsStore } from '@variants/stores/variantFlags'
import { useVariantCommentsStore } from '@variants/stores/variantComments'
import { useVariantAcmgRatingStore } from '@variants/stores/variantAcmgRating'
import { useSvFlagsStore } from '@svs/stores/strucvarFlags'
import { computed } from 'vue'

import CaseDetailsFlagIcon from '@cases/components/CaseDetail/FlagIcon.vue'

// Store-related.

const variantFlagsStore = useVariantFlagsStore()
const variantCommentsStore = useVariantCommentsStore()
const acmgRatingStore = useVariantAcmgRatingStore()
const svFlagsStore = useSvFlagsStore()
const svCommentsStore = useVariantCommentsStore()

// Constants.

const flagIds = [
  'flag_bookmarked',
  'flag_candidate',
  'flag_final_causative',
  'flag_for_validation',
  'flag_no_disease_association',
  'flag_segregates',
  'flag_doesnt_segregate',
] as const
type FlagIds = (typeof flagIds)[number]

// Component state.
const acmgCountByLevel = computed<{ [key: number]: number }>(() => {
  const result: { [key: number]: number } = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }
  for (const [_, acmgRating] of acmgRatingStore.caseAcmgRatings) {
    const level: number = acmgRating.classOverride ?? acmgRating.classAuto ?? 3
    result[level] += 1
  }
  return result
})

const buildComputedAnnoCountByFlag = (theList: Map<string, any>) => {
  return computed<{ [flagId in FlagIds]: number }>(() => {
    const result = {
      flag_bookmarked: 0,
      flag_candidate: 0,
      flag_final_causative: 0,
      flag_for_validation: 0,
      flag_no_disease_association: 0,
      flag_segregates: 0,
      flag_doesnt_segregate: 0,
    }
    for (const [_, varAnno] of theList) {
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
  variantFlagsStore.caseFlags,
)
const svAnnoCountByFlag = buildComputedAnnoCountByFlag(svFlagsStore.caseFlags)
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
            {{ acmgRatingStore.caseAcmgRatings.size }}
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
          <div class="col-1 text-right">
            {{ variantFlagsStore.caseFlags.size }}
          </div>
          <div class="col-8">
            <span
              v-for="flagId in flagIds"
              :key="`seqvar-flag-${flagId}`"
              class="mr-3"
            >
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
            {{ variantCommentsStore.caseComments.size }}
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
            <span
              v-for="flagId in flagIds"
              :key="`strucvar-flag-${flagId}`"
              class="mr-3"
            >
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
            {{ svCommentsStore.caseComments.size }}
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>
