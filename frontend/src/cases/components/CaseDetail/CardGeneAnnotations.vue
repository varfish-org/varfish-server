<script setup>
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'

const caseDetailsStore = useCaseDetailsStore()
</script>

<template>
  <div class="card mb-3 varfish-case-list-card flex-grow-1">
    <h5 class="card-header p-2 pl-2">
      <i-mdi-view-list-outline />
      Gene Annotations
    </h5>
    <table class="table table-striped table-hover">
      <thead>
        <tr>
          <th style="width: 10%" class="text-nowrap">Gene</th>
          <th style="width: 10px" class="text-nowrap">% at 20x</th>
          <th>message</th>
        </tr>
      </thead>
      <tbody>
        <template
          v-if="
            caseDetailsStore.geneAnnotations &&
            caseDetailsStore.geneAnnotations.length
          "
        >
          <tr
            v-for="geneAnnotation in caseDetailsStore.geneAnnotations"
            :key="`gene-annotation-${geneAnnotation.gene_symbol}`"
            class="{ 'text-danger': geneAnnotation.level === 'error', 'text-warning': geneAnnotation.level === 'warning', 'text-success': geneAnnotation.level === 'success', }"
          >
            <td>{{ geneAnnotation.gene_symbol }}</td>
            <td>{{ geneAnnotation.annotation.percentage_at_20x ?? '-' }}</td>
            <td>{{ geneAnnotation.annotation.message ?? '-' }}</td>
          </tr>
        </template>
        <tr v-else>
          <td colspan="3" class="text-muted text-center font-italic">
            No gene annotations (yet).
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
