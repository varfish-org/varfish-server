<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

import { displayName } from '@/varfish/helpers'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { useCaseListStore } from '@/cases/stores/caseList'
import { VigunoClient } from '@bihealth/reev-frontend-lib/api/viguno/client'

const emit = defineEmits(['updateCasePhenotypeTermsClick'])

const caseListStore = useCaseListStore()
const caseDetailsStore = useCaseDetailsStore()
const vigunoClient = new VigunoClient()

const termLabels = reactive({})

const allTerms = computed(() => {
  let result = []
  for (const phenotypeTerms of caseDetailsStore.casePhenotypeTerms ?? []) {
    if (phenotypeTerms?.terms) {
      result = result.concat(phenotypeTerms?.terms)
    }
  }
  fetchTermLabels(result)
  return result
})

const fetchingTerms = ref(false)

const fetchTermLabels = async (terms) => {
  if (fetchingTerms.value) {
    return // only fetch once
  }
  fetchingTerms.value = true
  for (const term of terms || allTerms.value) {
    if (!termLabels[term]) {
      let results
      if (term.startsWith('HP:')) {
        results = await vigunoClient.resolveHpoTermById(term)
      } else if (term.startsWith('OMIM:')) {
        const term2 = term.replace('OMIM:', '')
        results = await vigunoClient.resolveOmimTermById(term2)
      }
      if (results.result.length) {
        termLabels[term] = results[0].label
      }
    }
  }
  fetchingTerms.value = false
}

watch(
  () => termLabels.value,
  (_newValue, _oldValue) => {
    fetchTermLabels()
  },
)

onMounted(() => {
  fetchTermLabels()
})

const termsMap = computed(() => {
  const result = {}
  for (const member of caseDetailsStore.caseObj.pedigree) {
    result[member.name] = []
  }
  for (const phenotypeTerms of caseDetailsStore.casePhenotypeTerms ?? []) {
    const termList = phenotypeTerms?.terms || []
    result[phenotypeTerms.individual] = {
      sodar_uuid: phenotypeTerms.sodar_uuid,
      terms: termList.map((term) => {
        return {
          term,
          label: termLabels[term] ?? null,
        }
      }),
    }
  }
  return result
})

const userHasPerms = (perm) =>
  caseListStore.userPerms && caseListStore.userPerms.includes(perm)
</script>

<template>
  <div
    class="card mb-3 varfish-case-list-card flex-grow-1"
    style="overflow-y: auto !important; max-height: 300px"
  >
    <h5 class="card-header p-2">
      <i-mdi-file-tree />
      Phenotype and Disease Terms
      <div v-if="fetchingTerms" class="col-auto float-right">
        <i-fa-solid-circle-notch class="spin" />
      </div>
    </h5>
    <ul id="case-term-list" class="list-group list-group-flush list">
      <template v-if="caseDetailsStore.caseObj">
        <li
          v-for="member in caseDetailsStore.caseObj.pedigree"
          :key="`member-${member.name}`"
          class="list-group-item list-item pl-2"
        >
          <strong>{{ displayName(member.name) }}</strong>
          <template v-if="userHasPerms('cases.update_case')">
            &middot;
            <a
              href="#"
              @click.prevent="
                emit('updateCasePhenotypeTermsClick', {
                  casePhenotypeTermsUuid: termsMap[member.name].sodar_uuid,
                  individual: member.name,
                })
              "
            >
              update
            </a>
          </template>
          <br />
          <template v-if="termsMap[member.name]?.terms?.length">
            <div
              v-for="term in termsMap[member.name].terms"
              :key="`term-${term.term}`"
              @change="fetchTermLabels()"
            >
              {{ term.label || term.term }}
            </div>
          </template>
          <template v-else>
            <span class="text-muted font-italic">
              No phenotype / disease terms for individual.
            </span>
          </template>
        </li>
      </template>
      <li
        v-else
        class="list-group-item list-item row font-italic text-muted text-center"
      >
        No inviduals in case.
      </li>
    </ul>
  </div>
</template>

<style scoped>
.spin {
  animation-name: spin;
  animation-duration: 2000ms;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
