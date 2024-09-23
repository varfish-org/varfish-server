<script setup>
/**
 * A simple component for showing a modal confirmation dialog.
 *
 * You can configure it either by setting the props or handing the props to the show() method.
 *
 * You can react on the "confirm button clicked" event either by handling the "confirm" event
 * or use the Promise returned by show with its resolve function.  Both the event and the resolve
 * function will be passed the "extraData" value.
 */
import { reactive, ref } from 'vue'

import { randomString } from '@/varfish/common'
import ModalBase from '@/varfish/components/ModalBase.vue'
import { copy } from '@/varfish/helpers'

/** Define props, will be copied to propsCopy. */
const props = defineProps({
  title: {
    type: String,
    default: 'Please Confirm',
  },
  text: {
    type: String,
    default: null,
  },
  noHeader: {
    type: Boolean,
    default: false,
  },
  idSuffix: {
    type: String,
    default: randomString(),
  },
  isDanger: {
    type: Boolean,
    default: false,
  },
  extraData: {
    type: Object,
    default: null,
  },
})

/** Define the emits. */
const emit = defineEmits(['cancel', 'confirm'])

/** Copy of props to allow overriding with arguments of show(). */
const propsCopy = ref(copy(props))

/** Whether the confirm button is enabled (used if props.isDanger). */
const confirmEnabled = ref(false)

/** Whether the confirm button should be enabled. */
const enableButton = () => !propsCopy.value.isDanger || confirmEnabled.value

/** Ref to the inner modal. */
const innerModalRef = ref(null)

/** Whether the promise was resolved already. */
const promiseCompleted = ref(false)

/** Ref to the resolve function promise returned by show(). */
const resolveRef = ref(null)

// NB: it probably makes no sense to reject on cancel, but we emit the 'cancel' event nevertheless.
// /** Ref to the reject function promise returned by show(). */
// const rejectRef = ref(null)

/** Reset the inner state. */
const reset = () => {
  confirmEnabled.value = false
  promiseCompleted.value = false
  resolveRef.value = null
  // rejectRef.value = null
}

/** Show the modal. */
const show = (args = {}) => {
  propsCopy.value = reactive({
    ...props,
    ...args,
  })
  reset()
  innerModalRef.value.show()
  return new Promise(function (resolve /*, reject*/) {
    resolveRef.value = resolve
    // rejectRef.value = reject
  })
}

/** Hide the modal. */
const hide = () => {
  innerModalRef.value.hide()
}

/** Event handler for confirm button. */
const onConfirm = () => {
  if (!promiseCompleted.value) {
    // don't handle twice
    promiseCompleted.value = true
    resolveRef.value(propsCopy.value.extraData)
    emit('confirm', propsCopy.value.extraData)
    hide()
  }
}

/** Event handler for cancel button. */
const onCancel = () => {
  if (!promiseCompleted.value) {
    // don't handle twice
    // rejectRef.value(propsCopy.value.extraData)
    emit('cancel', propsCopy.value.extraData)
    hide()
  }
}

defineExpose({ show, hide })
</script>

<template>
  <ModalBase
    ref="innerModalRef"
    :title="propsCopy.title"
    :no-header="propsCopy.noHeader"
    @close="onCancel"
  >
    <template #default>
      <div v-if="propsCopy.text">
        {{ propsCopy.text }}
      </div>
      <div v-if="propsCopy.isDanger" class="{'pt-3': propsCopy.text}">
        <div class="custom-control custom-switch">
          <input
            :id="'checkbox-' + props.idSuffix"
            v-model="confirmEnabled"
            type="checkbox"
            class="custom-control-input"
          />
          <label
            class="custom-control-label"
            :for="'checkbox-' + props.idSuffix"
          >
            enable "confirm" button
          </label>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="ml-auto">
        <a
          class="btn mr-2"
          :class="{
            'btn-danger': propsCopy.isDanger,
            'btn-success': !propsCopy.isDanger,
            disabled: !enableButton(),
          }"
          href="#"
          @click.prevent="onConfirm()"
        >
          <i-mdi-check />
          Confirm
        </a>
        <a class="btn btn-secondary" @click="onCancel()">
          <i-mdi-close />
          Cancel
        </a>
      </div>
    </template>
  </ModalBase>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
