<script setup>
import { watch, ref, onMounted, nextTick, onBeforeMount } from 'vue'
import { useRouter } from 'vue-router'
import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import { VariantClient } from '@variants/api/variantClient'
import {
  DisplayColumns,
  DisplayConstraints,
  DisplayDetails,
  DisplayFrequencies,
} from '@variants/enums'

import FilterResultsTable from '@variants/components/FilterResultsTable.vue'
import SvFilterResultsTable from '@svs/components/SvFilterResultsTable.vue'

const router = useRouter()

const props = defineProps({
  /** The case UUID. */
  caseUuid: String,
})

const caseDetailsStore = useCaseDetailsStore()

/** The details columns to show. */
const displayDetails = ref(DisplayDetails.Coordinates.value)
/** The frequency columns to show. */
const displayFrequency = ref(DisplayFrequencies.GnomadExomes.value)
/** The constraint columns to show. */
const displayConstraint = ref(DisplayConstraints.GnomadPli.value)
/** The additional columns to display. */
const displayColumns = ref([DisplayColumns.Effect.value])

const showSmallVariantDetails = async (event) => {
  router.push({
    name: 'variant-details',
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
