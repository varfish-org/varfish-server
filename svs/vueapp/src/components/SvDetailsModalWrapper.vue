<script setup>
import { computed, ref } from 'vue'
import { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'

import { formatLargeInt } from '@varfish/helpers.js'

import SvDetails from './SvDetails.vue'

const props = defineProps(['svRecord', 'fetched', 'previousQueryDetails'])

const modalRef = ref(null)
const modalContentRef = ref(null)

const showModal = () => {
  $(modalRef.value).modal('show')
}

const downloadModalContent = async () => {
  const browserWidth = modalContentRef.value.clientWidth
  const browserHeight = modalContentRef.value.clientHeight
  const paperWidth = 190 // A4=210mm, 10mm horizontal margin

  const canvas = await html2canvas(modalContentRef.value)
  const imgData = canvas.toDataURL('image/png')

  const doc = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })
  doc.addImage(
    imgData,
    'PNG',
    10,
    10,
    190,
    (paperWidth / browserWidth) * browserHeight
  )
  doc.save('varfish-sv-info.pdf')
}

const svDescription = computed(() => {
  if (props.svRecord) {
    const start = formatLargeInt(props.svRecord.start)
    const end = formatLargeInt(props.svRecord.end)
    const result = `${props.svRecord.chromosome}:${start}-${end}:${props.svRecord.sv_type}`
    if (!result.startsWith('chr')) {
      return `chr${result}`
    } else {
      return result
    }
  }
})

defineExpose({
  showModal,
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
      <div class="modal-content" ref="modalContentRef">
        <div class="modal-header">
          <h3 class="modal-title" id="variantDetailsModalLabel">
            SV Details for
            <template v-if="props.svRecord">
              {{ svDescription }}
            </template>
            <span v-else>
              ...
              <i-fa-solid-circle-notch class="spin" />
            </span>
          </h3>
          <span class="close">
            <button
              type="button"
              class="btn btn-sm btn-outline-dark"
              @click="downloadModalContent"
            >
              <i-mdi-download />
              Download This
            </button>
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
          <SvDetails />
        </div>
      </div>
    </div>
  </div>
</template>
