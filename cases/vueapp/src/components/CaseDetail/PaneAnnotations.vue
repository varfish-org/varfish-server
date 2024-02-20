<script setup>
import { useRouter } from 'vue-router'

import FilterResultsTable from '@variants/components/FilterResultsTable.vue'
import SvFilterResultsTable from '@svs/components/SvFilterResultsTable.vue'

const router = useRouter()

const showSmallVariantDetails = async (event) => {
  router.push({
    name: 'seqvar-details',
    params: {
      row: event.smallvariantresultrow,
      selectedSection: event.selectedSection ?? null,
    },
  })
}

const showStructuralVariantDetails = async (event) => {
  router.push({
    name: 'sv-details',
    params: {
      row: event.svresultrow,
      selectedSection: event.selectedSection ?? null,
    },
  })
}
</script>

<template>
  <div class="row pt-3 pb-3 flex-grow-1 d-flex flex-column">
    <div class="col flex-grow-1 d-flex flex-column">
      <h5>Small Variant User Annotations</h5>
      <FilterResultsTable @variant-selected="showSmallVariantDetails" />
    </div>
  </div>
  <div class="row pt-3 pb-3 flex-grow-1 d-flex flex-column">
    <div class="col flex-grow-1 d-flex flex-column">
      <h5>Structural Variant User Annotations</h5>
      <SvFilterResultsTable @variant-selected="showStructuralVariantDetails" />
    </div>
  </div>
</template>
