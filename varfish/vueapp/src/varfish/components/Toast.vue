<script setup>
/**
 * A simple component to show a toast.
 *
 * You can configure it either by setting the props or handing the props to the show() method.
 */
import { onMounted, ref } from 'vue'
import { formatTimeAgo } from '@varfish/helpers.js'
import { copy } from '@varfish/helpers'

/** Define props, will be copied to propsCopy. */
const props = defineProps({
  title: {
    type: String,
    default: 'Title',
  },
  text: {
    type: String,
    default: 'Body',
  },
  level: {
    type: String,
    default: 'info',
  },
  delay: {
    type: Number,
    default: null,
  },
  autohide: {
    type: Boolean,
    default: true,
  },
})

/** Ref to the toast `<div>` element. */
const toastRef = ref(null)
/** The time when the toast was shown. */
const timeShown = ref(null)
/** String with "$time ago" value. */
const timeShownAgo = ref('')

/** Copy of props, so we can override with arguments to show. */
const propsCopy = ref(copy(props))

/** Show the toast. */
const show = (args = {}) => {
  propsCopy.value = {
    ...props,
    ...args,
  }
  timeShown.value = new Date()
  $(toastRef.value).toast('show') // show via JQuery
}

/** Explicitely hide the toast. */
const hide = () => {
  $(toastRef.value).toast('hide') // hide via JQuery
}

/** Compute the role attribute. */
const role = () => {
  if (['error', 'warning'].includes(props.level)) {
    return 'alert'
  } else if (['success', 'info'].includes(props.level)) {
    return 'status'
  }
}

/** Compute the aria-live attribute. */
const ariaLive = () => {
  if (['error', 'warning'].includes(props.level)) {
    return 'assertive'
  } else if (['success', 'info'].includes(props.level)) {
    return 'polite'
  }
}

onMounted(() => {
  setInterval(() => {
    if (timeShown.value) {
      timeShownAgo.value = formatTimeAgo(timeShown.value)
    }
  }, 100)
})

defineExpose({ show, hide })
</script>

<template>
  <div style="position: absolute; bottom: 1em; right: 1em">
    <div
      ref="toastRef"
      class="toast hide"
      aria-atomic="true"
      :role="role()"
      :aria-live="ariaLive()"
      :data-delay="propsCopy.delay"
      :data-autohide="propsCopy.autohide ? 'true' : 'false'"
    >
      <div class="toast-header">
        <i-mdi-check-bold
          v-if="propsCopy.level === 'success'"
          class="text-success"
        />
        <i-mdi-information
          v-if="propsCopy.level === 'info'"
          class="text-info"
        />
        <i-bi-exclamation-circle
          v-if="propsCopy.level === 'warning'"
          class="text-warning"
        />
        <i-mdi-close-bold
          v-if="propsCopy.level === 'error'"
          class="text-danger"
        />
        <strong
          class="ml-1 mr-auto"
          :class="{
            'text-success': propsCopy.level === 'success',
            'text-info': propsCopy.level === 'info',
            'text-warning': propsCopy.level === 'warning',
            'text-error': propsCopy.level === 'error',
          }"
        >
          {{ propsCopy.title }}
        </strong>
        <small class="text-muted">
          {{ timeShownAgo }}
        </small>
        <button
          type="button"
          class="ml-2 mb-1 close"
          data-dismiss="toast"
          aria-label="Close"
        >
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="toast-body">
        {{ propsCopy.text }}
      </div>
    </div>
  </div>
</template>
