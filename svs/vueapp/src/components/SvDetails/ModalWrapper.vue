<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { formatLargeInt } from '@varfish/helpers'
import { useSvDetailsStore } from '@svs/stores/svDetails'
import { useSvQueryStore } from '@svs/stores/svQuery'
import SvDetails from '@svs/components/SvDetails.vue'
import { SvClient } from '@svs/api/svClient'

const props = defineProps({
  visible: Boolean,
  resultRowUuid: String,
  selectedSection: String,
})

const router = useRouter()

/** Ref for the modal component. */
const modalRef = ref(null)

const svRecord = ref(null)

const svDetailsStore = useSvDetailsStore()
const svQueryStore = useSvQueryStore()

/** Return the label to show on top of the details modal. */
const svLabel = computed(() => {
  if (svRecord.value) {
    const start = formatLargeInt(svRecord.value.start)
    const end = formatLargeInt(svRecord.value.end)
    const result = `${svRecord.value.chromosome}:${start}-${end}:${svRecord.value.sv_type}`
    if (!result.startsWith('chr')) {
      return `chr${result}`
    } else {
      return result
    }
  }
})

/** Called when the modal is shown; will fetch variant details. */
const showModal = async () => {
  if (!modalRef.value) {
    return
  }

  $(modalRef.value).modal('show')

  await svQueryStore.initializeRes

  const svClient = new SvClient(svQueryStore.csrfToken)
  const resultRow = await svClient.retrieveSvQueryResultRow(props.resultRowUuid)
  svRecord.value = resultRow
  await svDetailsStore.fetchSvDetails(resultRow)
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
  },
)

/** Event handler called when the modal is hidden.
 *
 * This pushes a route to the variant filtration again.
 */
const modalHiddenHandler = () => {
  router.push({
    name: 'svs-filter',
    params: {
      case: svQueryStore.caseUuid,
      query: svQueryStore.previousQueryDetails.sodar_uuid,
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
        <div class="modal-header pt-1 pb-1">
          <h3 class="modal-title" id="variantDetailsModalLabel">
            SV Details for
            <template v-if="svRecord">
              {{ svLabel }}
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
        <div class="modal-body pt-0">
          <SvDetails
            :result-row-uuid="props.resultRowUuid"
            :selected-section="props.selectedSection"
          />
        </div>
      </div>
    </div>
  </div>
</template>
