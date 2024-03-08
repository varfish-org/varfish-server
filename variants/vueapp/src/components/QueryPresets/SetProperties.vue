<script setup>
/** Editor component for the query preset set properties.
 */

import { computed } from 'vue'
import { randomString } from '@varfish/common'

/** Define props. */
const props = defineProps({
  // eslint-disable-next-line vue/require-default-prop
  label: String,
  idSuffix: {
    type: String,
    default: randomString(),
  },
})

/** Define emits. */
const emit = defineEmits(['update:label'])

/** Helper wrapper for the v-model:label. */
const labelModel = computed({
  get() {
    return props.label
  },
  set(newValue) {
    emit('update:label', newValue)
  },
})
</script>

<template>
  <div class="mr-2 mt-2">
    <div class="form-group">
      <label :for="'label' + idSuffix"> Label </label>
      <input
        :id="'label' + props.idSuffix"
        v-model="labelModel"
        type="text"
        class="form-control"
        placeholder="PresetSet label"
      />
      <small id="emailHelp" class="form-text text-muted">
        The label to use for display
      </small>
    </div>
  </div>
</template>
