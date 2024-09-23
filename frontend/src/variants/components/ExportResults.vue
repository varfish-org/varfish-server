<script setup>
import ExportResultsButton from '@/variants/components/ExportResultsButton.vue'
</script>

<template>
  <div class="align-self-center ml-auto">
    <button
      id="filterDisplayOptions"
      class="btn btn-outline-secondary dropdown-toggle"
      type="button"
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
      <ExportResultsButton file-type="tsv" />
      <ExportResultsButton file-type="xlsx" />
      <ExportResultsButton file-type="vcf" />
    </div>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
