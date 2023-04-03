<script setup>
import VariantDetails from './VariantDetails.vue'
import { ref } from 'vue'

const props = defineProps(['smallVariant', 'fetched', 'previousQueryDetails'])

const components = {
  VariantDetails,
}

const smallVariantLabel = () => {
  const smallVariant = props.smallVariant
  const start = smallVariant.start.toLocaleString()
  return `${smallVariant.chromosome}:${start}${smallVariant.reference}>${smallVariant.alternative}`
}

const modalRef = ref(null)

const showModal = () => {
  $(modalRef.value).modal('show')
}

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
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title" id="variantDetailsModalLabel">
            Variant Details for
            <template v-if="props.smallVariant">
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
          <span v-if="props.fetched">
            <VariantDetails />
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
