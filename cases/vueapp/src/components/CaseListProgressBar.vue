<script setup>
import { CaseStates, useCasesStore } from '../stores/cases.js'
import { computed } from 'vue'

// Use the case store.
const casesStore = useCasesStore()

/** Return an object with key/counter int with the keys from CaseStates. */
const counters = computed(() => {
  const counters = Object.fromEntries(
    Object.keys(CaseStates).map((key) => [key, 0])
  )
  for (const caseObj of Object.values(casesStore.cases)) {
    counters[caseObj.status] += 1
  }
  return counters
})

/** Number of cases in the casesStore */
const caseCount = computed(() => Object.keys(casesStore.cases).length)

/** Helper to convert from case state to "bg-X" bootstrap CSS class. */
const stateBgColor = (state) => {
  return `bg-${CaseStates[state].color}`
}
</script>

<template>
  <div class="pull-left mr-3 font-weight-bold">Progress</div>
  <div class="progress" style="height: 2em">
    <template v-if="caseCount > 0">
      <template v-for="(value, name) in counters">
        <div
          v-if="value !== 0"
          class="progress-bar"
          :class="stateBgColor(name)"
          role="progressbar"
          :style="`width: ${(100 * value) / caseCount}%`"
        >
          {{ value }}/{{ caseCount }} ({{ (100 * value) / caseCount }}%) initial
        </div>
      </template>
    </template>
    <div
      v-else
      class="progress-bar bg-secondary font-italic"
      style="width: 100%"
    >
      no samples in project
    </div>
  </div>
</template>
