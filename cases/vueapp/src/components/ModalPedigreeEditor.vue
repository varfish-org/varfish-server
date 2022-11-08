<script setup>
/**
 * A component for showing a modal to edit pedigrees.
 *
 * You can configure it either by setting the props or handing the props to the show() method.
 *
 * You can react on the "confirm button clicked" event either by handling the "confirm" event
 * or use the Promise returned by show with its resolve function.  Both the event and the resolve
 * function will be passed the input and the "props.extraData" value.
 */

import { onMounted, reactive, ref } from 'vue'

import { useVuelidate } from '@vuelidate/core'

import ModalBase from '@varfish/components/ModalBase.vue'
import ModalPedigreeEditorRow from './ModalPedigreeEditorRow.vue'
import { randomString } from '@varfish/common.js'
import { copy } from '@varfish/helpers.js'

const props = defineProps({
  title: {
    type: String,
    default: 'Please Enter',
  },
  noHeader: {
    type: Boolean,
    default: false,
  },
  idSuffix: {
    type: String,
    default: randomString(),
  },
  modelValue: {
    type: Array,
    default: [],
  },
  modalClass: {
    type: String,
    default: 'modal-xl',
  },
})

/** Define the emits. */
const emit = defineEmits(['cancel', 'confirm', 'update:modelValue'])

/** Copy of props to allow overriding with arguments of show(). */
const propsCopy = ref(copy(props))

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
  promiseCompleted.value = false
  resolveRef.value = null
  // rejectRef.value = null
}

/** Show the modal. */
const show = (args) => {
  propsCopy.value = reactive({
    ...props,
    ...copy(args),
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
    resolveRef.value(propsCopy.value.modelValue)
    emit('confirm', propsCopy.value.modelValue)
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

// /** Create vuelidate object. */
const v$ = useVuelidate()

/** Initialize form value and vuelidate. */
onMounted(() => {
  v$.value.$touch()
})

defineExpose({ show, hide })
</script>

<template>
  <ModalBase
    ref="innerModalRef"
    :title="propsCopy.title"
    :no-header="propsCopy.noHeader"
    :modal-class="propsCopy.modalClass"
    @close="onCancel"
  >
    <template #default>
      <table class="table table-striped table-condensed">
        <thead>
          <tr>
            <th style="width: 20%">Name</th>
            <th style="width: 25%">Father</th>
            <th style="width: 25%">Mother</th>
            <th style="width: 15%">Sex</th>
            <th style="width: 15%">Affected</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(_row, index) in propsCopy.modelValue">
            <ModalPedigreeEditorRow
              :name="propsCopy.modelValue[index].name"
              :pedigree="propsCopy.modelValue"
              v-model:father="propsCopy.modelValue[index].father"
              v-model:mother="propsCopy.modelValue[index].mother"
              v-model:sex="propsCopy.modelValue[index].sex"
              v-model:affected="propsCopy.modelValue[index].affected"
            />
          </template>
        </tbody>
      </table>
    </template>
    <template #footer>
      <div class="ml-auto">
        <a
          class="btn btn-success mr-2"
          :class="{ disabled: v$.$error }"
          href="#"
          @click.prevent="onConfirm"
        >
          <i-mdi-check />
          Confirm
        </a>
        <a class="btn btn-secondary" @click.prevent="onCancel">
          <i-mdi-close />
          Cancel
        </a>
      </div>
    </template>
  </ModalBase>
</template>
