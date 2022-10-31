<script setup>
/**
 * A simple component for showing a modal dialogue for selecting a single value.
 *
 * You can configure it either by setting the props or handing the props to the show() method.
 *
 * The options are given as list of objects with "label" and "value" properties.
 */

import { onMounted, computed, reactive, ref } from 'vue'

import ModalBase from './ModalBase.vue'
import { randomString } from '../common.js'
import { useVuelidate } from '@vuelidate/core'
import { copy } from '@varfish/helpers'

const props = defineProps({
  title: {
    type: String,
    default: 'Please Select',
  },
  label: {
    type: String,
    default: null,
  },
  helpText: {
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
  defaultValue: {
    type: String,
    default: null,
  },
  options: {
    type: Array,
    default: null,
  },
  extraData: {
    type: Object,
    default: null,
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

/** Value from the input. */
const formState = reactive({
  inputValue: null,
})

/** Computed value for the rules, so we can react to props/propsCopy changes. */
const rules = computed(() => {
  return propsCopy.value?.rules || []
})

/** Reset the inner state. */
const reset = () => {
  promiseCompleted.value = false
  resolveRef.value = null
  formState.inputValue = propsCopy.value?.defaultValue ?? props.defaultValue
  // rejectRef.value = null
}

/** Show the modal. */
const show = (args) => {
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
    resolveRef.value(formState.inputValue, propsCopy.value.extraData)
    emit('confirm', formState.inputValue, propsCopy.value.extraData)
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

/** Create vuelidate object. */
const v$ = useVuelidate({ inputValue: rules }, formState)

/** Initialize form value and vuelidate. */
onMounted(() => {
  // formState.inputValue = propsCopy.value?.defaultValue ?? props.defaultValue
  v$.value.$touch()
})

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
      <div class="row">
        <div class="col">
          <div class="form-group">
            <label v-if="propsCopy.label" :for="'modal-input-' + idSuffix">
              {{ propsCopy.label }}
            </label>
            <select
              class="custom-select"
              v-model="v$.inputValue.$model"
              :id="'modal-input-' + idSuffix"
            >
              <option :value="null">Factory Presets</option>
              <option
                v-for="item in propsCopy.options"
                :key="item.value"
                :value="item.value"
              >
                {{ item.label }}
              </option>
            </select>
            <small v-if="propsCopy.helpText" class="form-text text-muted">
              {{ propsCopy.helpText }}
            </small>
          </div>
        </div>
      </div>
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
