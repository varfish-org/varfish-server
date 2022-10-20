<script setup>
import { displayName } from '@varfish/helpers.js'
import { useCaseDetailsStore } from '../stores/case-details.js'
import { computed } from 'vue'

const caseDetailsStore = useCaseDetailsStore()

const termsMap = computed(() => {
  const result = {}
  for (const member of caseDetailsStore.caseObj.pedigree) {
    result[member.name] = []
  }
  for (const phenotypeTerms of caseDetailsStore.caseObj.phenotype_terms) {
    result[phenotypeTerms.individual] = phenotypeTerms.terms
  }
  return result
})
</script>

<template>
  <div
    class="card mb-3 varfish-case-list-card flex-grow-1"
    style="overflow-y: auto !important; max-height: 300px"
  >
    <h5 class="card-header p-2 pl-2">
      <i-mdi-file-tree />
      Phenotype and Disease Terms
    </h5>
    <ul class="list-group list-group-flush list" id="case-term-list">
      <template v-if="caseDetailsStore.caseObj">
        <li
          v-for="member in caseDetailsStore.caseObj.pedigree"
          class="list-group-item list-item row"
        >
          <strong>{{ displayName(member.name) }}</strong
          ><br />
          <template v-if="termsMap[member.name].length">
            <div v-for="term in termsMap[member.name]">
              {{ term }}
            </div>
          </template>
          <template v-else>
            <span class="text-muted font-italic">
              No phenotype / disease terms for individual.
            </span>
          </template>
        </li>
      </template>
      <li v-else>No inviduals in case.</li>
    </ul>
  </div>
</template>
