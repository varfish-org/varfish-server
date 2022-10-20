<script setup>
import { computed } from 'vue'
import { useCasesStore } from '../stores/cases.js'
import { useRouter } from 'vue-router'

const props = defineProps({
  caseObj: Object,
})

/** The currently used router. */
const router = useRouter()

const casesStore = useCasesStore()
</script>

<template>
  <div>
    <!-- title etc. -->
    <div class="row sodar-pr-content-title pb-1">
      <!-- TODO buttons from sodar core -->
      <h2 class="sodar-pr-content-title">
        Case
        <small v-if="caseObj" class="text-muted">{{ caseObj.name }}</small>
        <small v-else>NO CASE</small>

        <a
          role="submit"
          class="btn btn-link mr-2 sodar-pr-btn-title sodar-pr-btn-copy-uuid sodar-copy-btn"
          id="sodar-pr-btn-copy-uuid"
          :data-clipboard-text="caseObj ? caseObj.sodar_uuid : ''"
          title="Copy UUID to clipboard"
          data-toggle="tooltip"
          data-placement="top"
        >
          <i-fa-solid-clipboard class="text-muted" />
        </a>
      </h2>

      <div class="ml-auto btn-group">
        <a class="btn btn-secondary" @click.prevent="router.push('/')">
          <i-mdi-arrow-left-circle />
          Back to Project
        </a>
        <a class="btn btn-primary" href="#">
          <i-mdi-filter />
          Filter Variants
        </a>
        <a class="btn btn-primary" href="#">
          <i-mdi-beta />
          Filter Variants (beta)
        </a>
        <a class="btn btn-primary" href="#">
          <i-mdi-filter-variant />
          Filter SVs
        </a>
        <a class="btn btn-secondary">
          <i-mdi-file-document-edit />
          Edit Pedigree
        </a>
        <a class="btn btn-secondary">
          <i-mdi-gender-male-female />
          Fix Sex
        </a>
        <a class="btn btn-danger">
          <i-mdi-delete-forever />
          Delete Case
        </a>
      </div>
    </div>

    <!-- inline help -->
    <div
      v-if="casesStore.showInlineHelp"
      class="alert alert-secondary small p-2"
    >
      <i-mdi-information />
      This is the case detail view. Here, you can inspect the case and its
      properties and perform edit operations on the case.
    </div>
  </div>
</template>
