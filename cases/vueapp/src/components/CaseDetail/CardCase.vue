<script setup>
import { computed, reactive } from 'vue'

import { CaseStates } from '@cases/stores/caseList'
import {
  displayName,
  formatTime,
  formatTimeAgo,
  formatLargeInt,
} from '@varfish/helpers'
import { useCaseDetailsStore } from '@cases/stores/caseDetails'

const emit = defineEmits(['editCaseStatusClick', 'editCaseNotesClick'])

// Store-related.

const caseDetailsStore = useCaseDetailsStore()

const caseObj = computed(() => {
  if (caseDetailsStore.caseObj) {
    return caseDetailsStore.caseObj
  } else {
    return reactive({ tags: [] })
  }
})

const individuals = computed(() => {
  if (!caseDetailsStore.caseObj) {
    return []
  } else {
    return caseDetailsStore.caseObj.pedigree.map((p) => displayName(p.name))
  }
})

const badgeStatusColor = computed(() => {
  if (caseObj.value && caseObj.value.status) {
    return 'badge-' + CaseStates.get(caseObj.value.status).color
  } else {
    return ''
  }
})
</script>

<template>
  <div class="card mb-3 varfish-case-list-card flex-grow-1">
    <div class="row card-header p-2 pl-2">
      <h5 class="col-auto ml-0 mr-0 mb-0">
        <i-mdi-card-account-details-outline />
        Case Details
      </h5>
      <div class="btn-group ml-auto">
        <a
          class="btn btn-sm btn-primary"
          href="#"
          @click.prevent="emit('editCaseStatusClick')"
        >
          <i-mdi-square-edit-outline />
          Edit Status
        </a>
        <a
          class="btn btn-sm btn-primary"
          href="#"
          @click.prevent="emit('editCaseNotesClick')"
        >
          <i-mdi-playlist-edit />
          Edit Notes
        </a>
      </div>
    </div>
    <ul class="list-group list-group-flush">
      <li class="list-group-item pl-0">
        <div class="row">
          <span class="col-3 text-nowrap font-weight-bold"> Case Name </span>
          <span class="col-3"> {{ caseObj.name }} </span>
          <span class="col-2 text-nowrap font-weight-bold"> Individuals </span>
          <span class="col-4">
            {{ individuals ? individuals.join(', ') : '-' }}
          </span>
        </div>
      </li>
      <li class="list-group-item pl-0">
        <div class="row">
          <span class="col-3 text-nowrap font-weight-bold"> Created At </span>
          <span class="col-3" :title="formatTimeAgo(caseObj.date_created)">
            {{ formatTime(caseObj.date_created) }}
          </span>
          <span class="col-2 text-nowrap font-weight-bold">
            Last Modified
          </span>
          <span class="col-4" :title="formatTimeAgo(caseObj.date_modified)">
            {{ formatTime(caseObj.date_modified) }}</span
          >
        </div>
      </li>
      <li class="list-group-item pl-0">
        <div class="row">
          <span class="col-3 text-nowrap font-weight-bold">
            Reference Genome
          </span>
          <span class="col-3"> {{ caseObj.release }} </span>
        </div>
      </li>
      <li class="list-group-item pl-0">
        <div class="row">
          <span class="col-3 text-nowrap font-weight-bold">
            Status, Notes, &amp; Tags
          </span>
          <span class="col-9">
            <h4>
              <span class="badge" :class="badgeStatusColor">
                {{ caseObj.status }}
              </span>
            </h4>
            <div v-if="caseObj && caseObj.tags.length">
              <span v-for="tag in caseObj.tags" class="badge badge-secondary">
                {{ tag }}
              </span>
            </div>
            <div>
              <em v-if="caseObj && caseObj.notes">{{ caseObj.notes }}</em>
              <em v-if="!caseObj || !caseObj.notes" class="text-muted"
                >No notes taken (yet).</em
              >
            </div>
          </span>
        </div>
      </li>
      <li class="list-group-item pl-0">
        <div class="row">
          <span class="col-3 text-nowrap font-weight-bold">
            Called Variants
          </span>
          <span class="col-3">
            {{ formatLargeInt(caseObj.num_small_vars) }}
          </span>
          <span class="col-2 text-nowrap font-weight-bold"> Called SVs </span>
          <span class="col-4">
            {{ formatLargeInt(caseObj.num_svs) }}
          </span>
        </div>
      </li>
      <li class="list-group-item pl-0">
        <div class="row">
          <span class="col-3 text-nowrap font-weight-bold">
            Annotated Variants
          </span>
          <span class="col-3">
            {{
              caseDetailsStore.varAnnos !== null
                ? caseDetailsStore.varAnnos.length
                : '-'
            }}
          </span>
          <span class="col-2 text-nowrap font-weight-bold">
            Annotated SVs
          </span>
          <span class="col-4">
            {{
              caseDetailsStore.varAnnos !== null
                ? caseDetailsStore.varAnnos.length
                : '-'
            }}
          </span>
        </div>
      </li>
    </ul>
  </div>
</template>
