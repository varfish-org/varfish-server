<script setup>
/**
 * A text area that allows for "semi-structured" input of value.
 *
 * This component allows to enter the user data as free text.  The component
 * can be configured to "tokenize" the input appropriately, e.g., take words
 * of non-whitespace text or grab only things that look like ontology terms.
 *
 * These words can then be subjected to validation via regular expressions
 * or (async) callback functions.  The textarea will provide the user with
 * visual feedback by highlighting the words and display error messages.
 *
 * Ideas for highlighting taken from here:
 *
 * - https://codersblock.com/blog/highlight-text-inside-a-textarea/
 */

import { computed, nextTick, onMounted, ref, watch } from 'vue'
import debounce from 'lodash.debounce'
import isEqual from 'lodash.isequal'

/** Props of the component. */
const props = defineProps([
  /** The component's model value. */
  'modelValue',
  /**
   * Definition on tokenizing.
   *
   * RegExp - regular expression, each match is a token
   * other - tokenize based on whitespace
   */
  'tokenize',
  /**
   * Definition on token validation
   *
   * null - all tokens are valid
   *
   * RegExp - match token with regexp, use `/^...$/` to ensure that all
   *   characters match
   *
   * Function - callback that gets the token text.  Can either return a
   *   Boolean that indicates whether there is a match or not or an
   *   Object.  The object must have the members `valid` (Boolean)
   *   and optionally a String `error` with validation error message.
   */
  'validate',
  /** HTML `id` for the textarea */
  'textareaId',
])

/**
 * The component's emitted events.
 */
const emit = defineEmits(['update:modelValue', 'input', 'validation'])

/**
 * The internal text value of the textarea.
 *
 * @type String
 */
const textValueRef = ref('')

/**
 * Whether validation is currently running in the background.
 */
const isValidationRunning = ref(false)

/** Return current tokens. */
const tokens = () => {
  if (!textValueRef.value) {
    return []
  } else {
    return textValueRef.value.replace(/\n$/g, '\n\n').match(tokenizeRegexp())
  }
}

/** Wrapper around `props.modelValue`. */
const modelValueWrapper = computed({
  get() {
    return props.modelValue
  },
  set(newValue) {
    const newValue2 = newValue || []
    if (!isEqual(tokens(), newValue2)) {
      // update internal text value if it changed
      textValueRef.value = newValue2.join(' ')
      runValidationAndUpdateBackdrop()
    }
    emit('update:modelValue', newValue2)
  },
})

/** Whether the `value` is valid. */
const isValueValid = ref(true)
/** List of error messages. */
const errorMessages = ref([])

/** Ref on the `<textarea>`. */
const textareaRef = ref(null)
/** Ref on the rwapper `<div>`. */
const wrapperRef = ref(null)
/** Ref on the backdrop `<div>`. */
const backdropRef = ref(null)
/** Ref on the highlights `<div>` within the backdrop `<div>`. */
const highlightsRef = ref(null)

/** Map token values to objects with `state`, `result`, and `promise` entry. */
const validationResults = {}

/** Update `isValidationRunning` */
const updateIsValidationRunning = () => {
  let result = false
  for (const entry of Object.values(validationResults)) {
    result = result || entry.state === 'resolving'
  }
  isValidationRunning.value = result
  nextTick()
}

/** Callback used for highlighting a text token depending on validation. */
const highlightToken = (token) => {
  if (!(token in validationResults)) {
    const cbResult = props.validate(token)
    if (cbResult === true || cbResult === false) {
      validationResults[token] = {
        state: 'resolved',
        result: {
          valid: cbResult,
        },
      }
    } else if (cbResult instanceof Promise) {
      validationResults[token] = {
        state: 'resolving',
        result: null,
        promise: new Promise(() => {
          cbResult.then(
            (value) => {
              validationResults[token].state = 'resolved'
              if (value === true || value === false) {
                validationResults[token].result = { valid: value }
              } else {
                validationResults[token].result = value
              }
              updateIsValidationRunning()
              runValidationAndUpdateBackdrop()
            },
            () => {
              validationResults[token].state = 'rejected'
              updateIsValidationRunning()
              runValidationAndUpdateBackdrop()
            },
          )
        }).then(),
      }
      updateIsValidationRunning()
    } else if ('valid' in cbResult) {
      validationResults[token].result = cbResult
    } else {
      throw new Error(
        'Invalid result, not boolean, or has valid, or is Promise! ' + cbResult,
      )
    }
  }

  let cssClass
  let label = null
  if (validationResults[token].state === 'resolving') {
    cssClass = 'waiting'
  } else if (validationResults[token].state === 'rejected') {
    cssClass = 'error'
  } else {
    cssClass = validationResults[token].result.valid ? 'good' : 'bad'
    label = validationResults[token].result.label
  }
  if (label) {
    return `<mark class="${cssClass}" title="${label}">${token}</mark>`
  } else {
    return `<mark class="${cssClass}">${token}</mark>`
  }
}

/** Collect error messages by field. */
const collectErrorMessages = (tokens) => {
  const tmp = {}
  for (const token of tokens) {
    const res = validationResults[token]
    if (res.state === 'resolved') {
      if (!res.result.valid) {
        let key = 'failed validation'
        if (res.result.error) {
          key = res.error
        }
        if (key in tmp) {
          tmp[key].push(token)
        } else {
          tmp[key] = [token]
        }
      }
    } else if (res.state === 'rejected') {
      const key = 'error during validation'
      if (key in tmp) {
        tmp[key].push(token)
      } else {
        tmp[key] = [token]
      }
    }
  }

  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1)
  }

  const result = []
  for (const [msg, fields] of Object.entries(tmp)) {
    result.push(capitalizeFirstLetter(msg) + ': ' + fields.join(', ') + '.')
  }
  return result
}

/** Return regexp to use for tokenization. */
const tokenizeRegexp = () => {
  const defaultTokenizeRegexp = /(\S+)/g
  return props.tokenize instanceof RegExp
    ? props.tokenize
    : defaultTokenizeRegexp
}

/** Helper function that runs validation on the tokens and runs highlighting. */
const _runValidationAndUpdateBackdrop = () => {
  const highlightedHtml = textValueRef.value
    .replace(/\n$/g, '\n\n')
    .replace(tokenizeRegexp(), highlightToken)
  const theTokens = tokens()
  if (theTokens) {
    errorMessages.value = collectErrorMessages(theTokens)
  } else {
    errorMessages.value = []
  }
  isValueValid.value = Object.keys(errorMessages.value).length === 0
  highlightsRef.value.innerHTML = highlightedHtml
  emit('validation')
}

/** The debounced version of `_runValidationAndUpdateBackdrop`. */
const runValidationAndUpdateBackdrop = debounce(
  _runValidationAndUpdateBackdrop,
  200,
  {
    leading: true,
    maxWait: 2,
    trailing: true,
  },
)

/** Event handler that keeps the textarea's and backdrop's scrolling in sync. */
const updateScroll = () => {
  backdropRef.value.scrollTop = textareaRef.value.scrollTop
}

/** Event handler that keeps the textarea's parent size in sync. */
const updateSize = () => {
  wrapperRef.value.style.height = textareaRef.value.style.height
}

/** Event handler for input that ensures update of the backdrop. */
const handleInput = () => {
  modelValueWrapper.value = tokens()
  emit('input')
  runValidationAndUpdateBackdrop()
}

/** Update internal value and run validation/highlighting on mounting. */
onMounted(() => {
  modelValueWrapper.value = props.modelValue
  runValidationAndUpdateBackdrop()
})

/** Whether the value of this component is valid.  This function is exposed. */
const isValid = () => isValueValid.value

/** Whether or not the component is currently validating.  This function is
 * exposed.
 */
const isValidating = () => isValidationRunning.value

/** Watch changes of props.modelValue. */
watch(
  () => props.modelValue,
  (newValue, _oldValue) => {
    modelValueWrapper.value = newValue
  },
)

/** Define the exposed functions. */
defineExpose({
  isValid,
  isValidating,
  tokens,
})
</script>

<template>
  <div>
    <!-- Reproduce is-invalid on wrapper to make .invalid-feedback render correctly. -->
    <div
      ref="wrapperRef"
      class="tokenizing-textarea-wrapper"
      :class="{
        'is-invalid': !isValid(),
      }"
    >
      <div ref="backdropRef" class="textarea-backdrop form-control">
        <small
          v-if="isValidationRunning.value"
          class="text-muted"
          style="position: absolute; right: 5px; top: 5px"
        >
          <i-fa-solid-circle-notch class="spin" />
          validating...
        </small>
        <div
          ref="highlightsRef"
          id="textarea-highlights"
          class="textarea-highlights"
        ></div>
      </div>
      <textarea
        ref="textareaRef"
        v-model="textValueRef"
        class="position-absolute form-control textarea-highlighted"
        :class="{
          'is-invalid': !isValid(),
        }"
        :id="textareaId"
        @input="handleInput()"
        @scroll="updateScroll()"
        @mouseup="updateSize()"
      ></textarea>
    </div>
    <div v-for="errorMessage in errorMessages" class="invalid-feedback">
      {{ errorMessage }}
    </div>
  </div>
</template>

<style>
.textarea-backdrop {
  position: absolute;
  z-index: 1;
  border: 1px solid #ffffffff;
  border-radius: 6px;
  background-color: #fff;
  overflow: auto;
  pointer-events: none;
  transition: transform 1s;

  margin: 0;
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;

  font-style: normal;
  font-variant-caps: normal;
  font-variant-ligatures: normal;
  font-variant-numeric: normal;
  font-stretch: 100%;
  letter-spacing: normal;
  word-spacing: 0px;
  overflow-wrap: break-word;
  height: 200px;
}

.textarea-highlights {
  white-space: pre-wrap;
  z-index: 10;
  word-wrap: break-word;
  color: #ffffff00;
  padding-left: -1px;
}

.tokenizing-textarea-wrapper {
  position: relative;
  height: 200px;
}

textarea.textarea-highlighted,
textarea.textarea-highlighted:focus {
  z-index: 2;
  background: transparent;
  height: 200px;
}

.textarea-highlights mark {
  padding: 0px !important;
}

mark.good {
  border-radius: 2px;
  color: transparent;
  background-color: #71a57199;
}

mark.bad {
  border-radius: 2px;
  color: transparent;
  background-color: #ff676799;
}

mark.waiting {
  border-radius: 2px;
  color: transparent;
  background-color: rgba(80, 76, 76, 0.6);
}

mark.error {
  border-radius: 2px;
  color: transparent;
  background-color: red;
}

.spin {
  animation-name: spin;
  animation-duration: 2000ms;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
