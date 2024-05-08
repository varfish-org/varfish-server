<script setup>
// eslint-disable
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
import isEqual from 'fast-deep-equal'

/** Props of the component. */
const props = defineProps({
  /** The component's model value. */
  // eslint-disable-next-line vue/require-default-prop
  modelValue: Object,
  /**
   * Definition on tokenizing.
   *
   * RegExp - regular expression, each match is a token
   * other - tokenize based on whitespace
   */
  // eslint-disable-next-line vue/require-default-prop
  tokenize: RegExp,
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
  // eslint-disable-next-line vue/require-default-prop
  validate: Function,
  /** HTML `id` for the textarea */
  // eslint-disable-next-line vue/require-default-prop
  textareaId: String,
})

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

/**
 * List of invalid tokens
 */
const invalidTokens = ref([])

/** Return current tokens. */
const tokens = () => {
  if (!textValueRef.value) {
    return []
  } else {
    return textValueRef.value.replace(/\n$/g, '\n\n').match(tokenizeRegexp())
  }
}

const htmlTokens = ref({})

/** Wrapper around `props.modelValue`. */
const modelValueWrapper = computed({
  get() {
    return props.modelValue
  },
  set(newValue) {
    const newValue2 = newValue || []
    emit('update:modelValue', newValue2)
    if (!isEqual(tokens(), newValue2)) {
      // update internal text value if it changed
      textValueRef.value = newValue2.join(' ')
      runValidation()
    }
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

/** Callback used for highlighting a text token depending on validation. */
const highlightTokens = (tokenListBatch) => {
  htmlTokens.value = {}
  if (
    !tokenListBatch['genepanel'][0].length &&
    !tokenListBatch['other'][0].length
  ) {
    return
  }
  Object.keys(tokenListBatch).forEach((typ) => {
    for (let i = 0; i < tokenListBatch[typ].length; ++i) {
      tokenListBatch[typ][i].forEach((token) => {
        htmlTokens.value[token] = 'waiting'
      })
    }
  })
  Object.keys(tokenListBatch).forEach((typ) => {
    for (let i = 0; i < tokenListBatch[typ].length; ++i) {
      props.validate(tokenListBatch[typ][i], typ).then((result) => {
        tokenListBatch[typ][i].forEach((token) => {
          if (typ === 'genepanel') {
            if (token in result && result[token] === 'active') {
              htmlTokens.value[token] = 'good'
            } else {
              htmlTokens.value[token] = 'bad'
            }
          } else {
            if ('genes' in result) {
              if (!(token in result.genes) || result.genes[token] === null) {
                htmlTokens.value[token] = 'bad'
              } else {
                htmlTokens.value[token] = 'good'
              }
            } else {
              if (token in result && result[token].valid) {
                htmlTokens.value[token] = 'good'
              } else {
                htmlTokens.value[token] = 'bad'
              }
            }
          }
        })
      })
    }
  })
}

const highlightToken = (token) => {
  return `<mark class="${htmlTokens.value[token]}">${token}</mark>`
}

const _runUpdateBackdrop = () => {
  isValidationRunning.value = false
  isValueValid.value = true
  for (const [key, value] of Object.entries(htmlTokens.value)) {
    isValidationRunning.value = isValidationRunning.value || value === 'waiting'
    isValueValid.value = isValueValid.value && value !== 'bad'
    if (isValueValid.value === false) {
      invalidTokens.value.push(key)
    }
  }
  highlightsRef.value.innerHTML = textValueRef.value
    .replace(/\n$/g, '\n\n')
    .replace(tokenizeRegexp(), highlightToken)
  if (isValidationRunning.value) {
    runUpdateBackdrop()
  }
}

const runUpdateBackdrop = debounce(_runUpdateBackdrop, 200, {
  leading: true,
  maxWait: 2,
  trailing: true,
})

/** Return regexp to use for tokenization. */
const tokenizeRegexp = () => {
  const defaultTokenizeRegexp = /(\S+)/g
  return props.tokenize instanceof RegExp
    ? props.tokenize
    : defaultTokenizeRegexp
}

/** Helper function that runs validation on the tokens and runs highlighting. */
const runValidation = () => {
  let runningLength = 0
  let runningLengthGenepanel = 0
  const batchSize = 1000
  let batchCount = 0
  let batchCountGenepanel = 0
  const tokenListBatch = {
    genepanel: [[]],
    other: [[]],
  }
  modelValueWrapper.value.forEach((token) => {
    if (token === '' || token === ' ') {
      return
    }
    if (token.startsWith('GENEPANEL:')) {
      runningLengthGenepanel += token.length
      if (runningLengthGenepanel <= batchSize) {
        tokenListBatch['genepanel'][batchCountGenepanel].push(token)
      } else {
        batchCountGenepanel += 1
        tokenListBatch['genepanel'].push([token])
        runningLengthGenepanel = token.length
      }
    } else {
      runningLength += token.length
      if (runningLength <= batchSize) {
        tokenListBatch['other'][batchCount].push(token)
      } else {
        batchCount += 1
        tokenListBatch['other'].push([token])
        runningLength = token.length
      }
    }
  })
  highlightTokens(tokenListBatch)
  runUpdateBackdrop()
}

/** Event handler that keeps the textarea's and backdrop's scrolling in sync. */
const updateScroll = () => {
  backdropRef.value.scrollTop = textareaRef.value.scrollTop
}

/** Event handler that keeps the textarea's parent size in sync. */
const updateSize = () => {
  wrapperRef.value.style.height = textareaRef.value.style.height
}

/** Event handler for input that ensures update of the backdrop. */
const handleInput = async () => {
  modelValueWrapper.value = tokens()
  await nextTick()
  emit('input')
  runValidation()
}

/** Update internal value and run validation/highlighting on mounting. */
onMounted(() => {
  modelValueWrapper.value = props.modelValue
  runValidation()
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
  invalidTokens,
  tokens,
})
</script>

<template>
  <!-- eslint-disable -->
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
          id="textarea-highlights"
          ref="highlightsRef"
          class="textarea-highlights"
        ></div>
      </div>
      <textarea
        :id="textareaId"
        ref="textareaRef"
        v-model="textValueRef"
        class="position-absolute form-control textarea-highlighted"
        :class="{
          'is-invalid': !isValid(),
        }"
        @input="handleInput()"
        @scroll="updateScroll()"
        @mouseup="updateSize()"
      ></textarea>
    </div>
    <div v-for="errorMessage in errorMessages" class="invalid-feedback">
      {{ errorMessage }}
    </div>
    <span v-for="invalidToken in invalidTokens" class="invalid-feedback">
      {{ invalidToken }}
    </span>
  </div>
  <!-- eslint-enable -->
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

<style scoped>
.form-control.is-invalid,
.pass,
.confirmpass:invalid {
  background-image: none !important;
  padding: 0.375rem 0.75rem !important;
}
</style>
