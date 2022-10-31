<script setup>
/** A simple bootstrap-driven modal.
 */

import { ref } from 'vue'

/** Define the props. */
const props = defineProps({
  title: String,
  noHeader: {
    type: Boolean,
    default: false,
  },
  modalClass: String,
})

/** Define the emit. */
const emit = defineEmits(['close'])

/** Ref to modal element. */
const modalRef = ref(null)

/** Show the modal. */
const show = () => {
  $(modalRef.value).modal('show')
  $(modalRef.value).on('hidden.bs.modal', (_event) => {
    emit('close')
  })
}

/** Hide the modal. */
const hide = () => {
  $(modalRef.value).modal('hide')
}

defineExpose({ show, hide })
</script>

<template>
  <div ref="modalRef" class="modal fade">
    <div
      class="modal-dialog modal-dialog-scrollable"
      :class="modalClass"
      role="document"
    >
      <div class="modal-content">
        <div v-if="!props.noHeader" class="modal-header">
          <slot name="header">
            <h5 v-if="props.title" class="modal-title">
              {{ props.title }}
            </h5>
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </slot>
        </div>
        <div class="modal-body">
          <slot> The modal's body. </slot>
        </div>
        <div class="modal-footer">
          <slot name="footer"></slot>
        </div>
      </div>
    </div>
  </div>
</template>
