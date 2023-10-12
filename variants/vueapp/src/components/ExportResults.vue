<script setup>
import ExportResultsButton from '@variants/components/ExportResultsButton.vue'
</script>

<template>
  <div class="align-self-center ml-auto">
    <button
      class="btn btn-outline-secondary dropdown-toggle"
      type="button"
      id="filterDisplayOptions"
      data-toggle="dropdown"
      aria-haspopup="true"
      aria-expanded="false"
    >
      Export
    </button>
    <div
      class="dropdown-menu dropdown-menu-right"
      aria-labelledby="filterDisplayOptions"
    >
      <ExportResultsButton fileType="tsv" />
      <ExportResultsButton fileType="xlsx" />
      <ExportResultsButton fileType="vcf" />
    </div>
  </div>
</template>
