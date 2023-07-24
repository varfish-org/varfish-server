<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import variantsApi from '@variants/api/variants.js'
import VariantDetails from '@variants/components/VariantDetails.vue'
import { useFilterQueryStore } from '@variants/stores/filterQuery.js'
import { useVariantDetailsStore } from '@variants/stores/variantDetails.js'

const props = defineProps({
  visible: Boolean,
  resultRowUuid: String,
  selectedTab: String,
})

const router = useRouter()

/** Ref for the modal component. */
const modalRef = ref(null)

const smallVariant = ref(null)

const variantDetailsStore = useVariantDetailsStore()
const filterQueryStore = useFilterQueryStore()

/** Return the label to show on top of the details modal. */
const smallVariantLabel = () => {
  const theVar = smallVariant.value
  const start = theVar.start.toLocaleString()
  return `${theVar.chromosome}:${start}${theVar.reference}>${theVar.alternative}`
}

/** Called when the modal is shown; will fetch variant details. */
const showModal = async () => {
  if (!modalRef.value) {
    return
  }

  $(modalRef.value).modal('show')

  await filterQueryStore.initializeRes

  const resultRow = await variantsApi.retrieveQueryResultRow(
    filterQueryStore.csrfToken,
    props.resultRowUuid
  )
  smallVariant.value = resultRow.payload
  variantDetailsStore.fetchVariantDetails(
    resultRow.payload,
    filterQueryStore.previousQueryDetails.query_settings.database_select
  )
}

/** Watch the "visible" prop and map to jQuery calls. */
watch(
  [() => props.visible, () => props.resultRowUuid],
  async ([newVisible, _oldVisible], [_newUuid, _oldUuid]) => {
    if (!modalRef.value) {
      return
    }

    if (newVisible === true) {
      showModal()
    } else {
      $(modalRef.value).modal('hide')
    }
  }
)

/** Event handler called when the modal is hidden.
 *
 * This pushes a route to the variant filtration again.
 */
const modalHiddenHandler = () => {
  router.push({
    name: 'variants-filter',
    params: {
      case: filterQueryStore.caseUuid,
      query: filterQueryStore.previousQueryDetails.sodar_uuid,
    },
  })
}

onMounted(() => {
  // Ensure that the modal is shown when the component is initialized with visible=True
  if (props.visible) {
    showModal()
  }
  // Register handler for the modal disappearing
  $(modalRef.value).on('hide.bs.modal', modalHiddenHandler)
})
</script>

<template>
  <div
    class="modal fade"
    ref="modalRef"
    tabindex="-1"
    aria-labelledby="variantDetailsModalLabel"
    aria-hidden="true"
    style="z-index: 10000"
  >
    <div
      class="modal-dialog modal-dialog-scrollable modal-xl"
      role="document"
      style="max-width: 100%; margin: 10px"
    >
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title" id="variantDetailsModalLabel">
            Variant Details for
            <template v-if="smallVariant">
              {{ smallVariantLabel() }}
            </template>
            <span v-else>
              ...
              <i-fa-solid-circle-notch class="spin" />
            </span>
          </h3>
          <span class="close">
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
            >
              <span
                class="badge badge-dark font-weight-light mr-2"
                style="font-size: 60%"
              >
                Shortcut: Esc
              </span>
              <span aria-hidden="true">&times;</span>
            </button>
          </span>
        </div>
        <div class="modal-body">
          <span v-if="variantDetailsStore.fetched">
            <VariantDetails
              :result-row-uuid="props.resultRowUuid"
              :selected-tab="props.selectedTab"
            />
          </span>
          <div v-else class="alert alert-info">
            <i-fa-solid-circle-notch class="spin" />
            <strong>Loading details ...</strong>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
