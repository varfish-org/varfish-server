<script setup lang="ts">
import { useCaseListStore } from '@/cases/stores/caseList'
import UiToggleMaxButton from '@/varfish/components/UiToggleMaxButton/UiToggleMaxButton.vue'

const caseListStore = useCaseListStore()
</script>

<template>
  <!-- title etc. -->
  <div class="row sodar-pr-content-title pb-1">
    <!-- TODO buttons from sodar core -->
    <h2 class="sodar-pr-content-title">
      Listing Cases for Project
      <small class="text-muted">{{
        caseListStore.project?.title ?? 'PROJECT MISSING'
      }}</small>

      <a
        id="sodar-pr-btn-copy-uuid"
        role="submit"
        class="btn btn-link mr-2 sodar-pr-btn-title sodar-pr-btn-copy-uuid sodar-copy-btn"
        data-clipboard-text="{{ caseListStore.caseUuid }}"
        title="Copy UUID to clipboard"
        data-toggle="tooltip"
        data-placement="top"
      >
        <i-fa-solid-clipboard class="text-muted" />
      </a>
    </h2>

    <div class="ml-auto btn-group">
      <a
        class="btn btn-secondary"
        :href="`/project/${caseListStore.project?.sodar_uuid ?? 'no-uuid'}`"
      >
        <i-mdi-arrow-left-circle />
        Back to Project
      </a>
      <UiToggleMaxButton />
    </div>
  </div>

  <!-- inline help -->
  <div
    v-if="caseListStore.showInlineHelp"
    class="alert alert-secondary small p-2"
  >
    <i-mdi-information />
    This is the case list view of the case management app. You can toggle these
    gray boxes with verbose information using the
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
