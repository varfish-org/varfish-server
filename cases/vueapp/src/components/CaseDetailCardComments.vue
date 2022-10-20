<script setup>
import { formatTime } from '@varfish/helpers.js'
import { useCaseDetailsStore } from '../stores/case-details.js'

const caseDetailStore = useCaseDetailsStore()
</script>

<template>
  <div
    class="card mb-3 varfish-case-list-card flex-grow-1"
    style="overflow-y: auto !important; max-height: 300px"
  >
    <h5 class="card-header p-2 pl-2">
      <i-mdi-comment-multiple />
      Case Comments ({{
        caseDetailStore.caseComments ? caseDetailStore.caseComments.length : 0
      }})
    </h5>
    <ul
      class="list-group list-group-flush list"
      style="overflow-y: auto !important; max-height: 300px"
      id="case-comment-list"
    >
      <template
        v-if="
          caseDetailStore.caseComments &&
          caseDetailStore.caseComments.length > 0
        "
      >
        <li
          v-for="caseComment in caseDetailStore.caseComments"
          class="list-group-item list-item"
        >
          <div>
            <span class="small text-muted">
              <strong>{{ caseComment.user }}</strong>
              {{ formatTime(caseComment.date_created) }}
            </span>
            <div class="ml-3 font-italic">{{ caseComment.comment }}</div>
          </div>
        </li>
      </template>
      <li
        v-else
        class="list-group-item list-item text-center text-muted font-italic"
      >
        No case comments (yet).
      </li>
    </ul>
  </div>
</template>
