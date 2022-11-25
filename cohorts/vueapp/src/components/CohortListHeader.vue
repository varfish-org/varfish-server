<script setup>
import { computed } from 'vue'

import { useCohortsStore } from '@cohorts/stores/cohorts.js'

const cohortsStore = useCohortsStore()

const projectTitle = computed(() =>
  cohortsStore.project ? cohortsStore.project.title : 'PROJECT MISSING'
)

const projectUuid = computed(() =>
  cohortsStore.project ? cohortsStore.project.sodar_uuid : 'no-uuid'
)

/** Define emits. */
const emit = defineEmits(['createCohortClick'])
</script>

<template>
  <!-- title etc. -->
  <div class="row sodar-pr-content-title pb-1">
    <!-- TODO buttons from sodar core -->
    <h2 class="sodar-pr-content-title">
      Listing Cohorts for Project
      <small class="text-muted">{{ projectTitle }}</small>
    </h2>

    <div class="ml-auto btn-group">
      <a class="btn btn-secondary" :href="'/project/' + projectUuid">
        <i-mdi-arrow-left-circle />
        Back to Project
      </a>
      <a class="btn btn-primary" @click.prevent="emit('createCohortClick')">
        <i-mdi-plus-circle />
        Create Cohort
      </a>
    </div>
  </div>

  <!-- inline help -->
  <div
    v-if="cohortsStore.showInlineHelp"
    class="alert alert-secondary small p-2"
  >
    <i-mdi-information />
    This is the cohort list view of the cohort management app. You can toggle
    these gray boxes with verbose information using the
    <span class="badge badge-primary">
      <i-mdi-toggle-switch-outline style="scale: 200%" class="mr-2 ml-1" />
      <i-fa-solid-info />
    </span>
    switch on the top. You can change between simpler and more complex/powerful
    mode using the
    <span class="badge badge-primary">
      <i-mdi-form-dropdown style="scale: 150%" class="mr-2 ml-1" />
      <i-mdi-podium />
    </span>
    input next to it.
  </div>
</template>
