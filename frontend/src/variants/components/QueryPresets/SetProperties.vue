<script setup>
/** Editor component for the query preset set properties.
 */
import { computed } from 'vue'

import { randomString } from '@/varfish/common'

/** Define props. */
const props = defineProps({
  // eslint-disable-next-line vue/require-default-prop
  label: String,
  defaultPresetSet: Boolean,
  currentDefaultPresetSet: String,
  idSuffix: {
    type: String,
    default: randomString(),
  },
})

/** Define emits. */
const emit = defineEmits(['update:label', 'update:defaultPresetSet'])

/** Helper wrapper for the v-model:label. */
const labelModel = computed({
  get() {
    return props.label
  },
  set(newValue) {
    emit('update:label', newValue)
  },
})

const defaultPresetSetModel = computed({
  get() {
    return props.defaultPresetSet
  },
  set(newValue) {
    emit('update:defaultPresetSet', newValue)
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
  <div class="mr-2 mt-2">
    <div class="form-check">
      <input
        :id="'defaultPresetSet' + props.idSuffix"
        v-model="defaultPresetSetModel"
        class="form-check-input"
        type="checkbox"
      />
      <label class="form-check-label" :for="'defaultPresetSet' + idSuffix">
        Set as Default PresetSet for Project
        <span v-if="currentDefaultPresetSet" class="text-success">
          [{{ currentDefaultPresetSet }}]
        </span>
        <span v-else class="text-muted"> [None] </span>
      </label>
    </div>
    <small id="emailHelp" class="form-text text-muted">
      Make the preset set default for the project. Preset sets individually
      applied to a case are not overridden.
    </small>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
