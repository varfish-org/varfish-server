<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

import { displayName } from '@varfish/helpers.js'
import { useCaseDetailsStore } from '../stores/case-details.js'
import { useCasesStore } from '@cases/stores/cases.js'

const emit = defineEmits(['updateCasePhenotypeTermsClick'])

const casesStore = useCasesStore()
const caseDetailsStore = useCaseDetailsStore()

const termLabels = reactive({})

const props = defineProps({
  apiEndpoint: {
    type: String,
    default: '/variants/hpo-terms-api/',
  },
  csrfToken: String,
})

const allTerms = computed(() => {
  let result = []
  for (const phenotypeTerms of caseDetailsStore?.caseObj?.phenotype_terms ??
    []) {
    if (phenotypeTerms?.terms) {
      result = result.concat(phenotypeTerms?.terms)
    }
  }
  fetchTermLabels(result)
  return result
})

const fetchHpoTerms = async (query) => {
  const queryArg = encodeURIComponent(query)
  const response = await fetch(`${props.apiEndpoint}?query=${queryArg}`, {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    'X-CSRFToken': props.csrfToken,
  })
  const results = await response.json()
  const data = results.map(({ id, name }) => {
    return {
      label: `${id} - ${name}`,
      value: {
        term_id: id,
        name,
      },
    }
  })

  return data
}

const fetchingTerms = ref(false)

const fetchTermLabels = async (terms) => {
  if (fetchingTerms.value) {
    return // only fetch once
  }
  fetchingTerms.value = true
  for (const term of terms || allTerms.value) {
    if (!termLabels[term]) {
      const result = await fetchHpoTerms(term)
      if (result.length) {
        termLabels[term] = result[0].label
      }
    }
  }
  fetchingTerms.value = false
}

watch(
  () => termLabels.value,
  (_newValue, _oldValue) => {
    fetchTermLabels()
  }
)

onMounted(() => {
  fetchTermLabels()
})

const termsMap = computed(() => {
  const result = {}
  for (const member of caseDetailsStore.caseObj.pedigree) {
    result[member.name] = []
  }
  for (const phenotypeTerms of caseDetailsStore.caseObj.phenotype_terms) {
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
  casesStore.userPerms && casesStore.userPerms.includes(perm)
</script>

<template>
  <div
    class="card mb-3 varfish-case-list-card flex-grow-1"
    style="overflow-y: auto !important; max-height: 300px"
  >
    <div class="row card-header p-2 pl-2">
      <h5 class="col-auto">
        <i-mdi-file-tree />
        Phenotype and Disease Terms
      </h5>
      <div v-if="fetchingTerms" class="col-auto ml-auto">
        <i-fa-solid-circle-notch class="spin" />
      </div>
    </div>
    <ul class="list-group list-group-flush list" id="case-term-list">
      <template v-if="caseDetailsStore.caseObj">
        <li
          v-for="member in caseDetailsStore.caseObj.pedigree"
          class="list-group-item list-item row"
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
            <div v-for="term in termsMap[member.name].terms">
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
