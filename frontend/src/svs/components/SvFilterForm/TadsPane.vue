<script setup>
import { useVuelidate } from '@vuelidate/core'
import { computed, onMounted } from 'vue'

// Define the component's props.
const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  querySettings: Object,
})

// Return JSON string with settings from this tab to be displayed in "dev" mode.
const dumpTads = () => {
  const result = {}
  for (const [key, value] of Object.entries(props.querySettings)) {
    if (['tad_set'].includes(key)) {
      result[key] = value
    }
  }
  return JSON.stringify(result)
}

// Define validation rules.
const rules = {
  tad_set: {
    $autoDirty: true,
  },
}

// Helper function to build wrappers that catch the case of props.querySettings not being set.
const _vuelidateWrappers = (keys) =>
  Object.fromEntries(
    keys.map((key) => [
      key,
      computed({
        get() {
          return !props.querySettings ? null : props.querySettings[key]
        },
        set(newValue) {
          if (props.querySettings) {
            props.querySettings[key] = newValue
          }
        },
      }),
    ]),
  )

// Define the form state.
const formState = {
  ..._vuelidateWrappers(['tad_set']),
}

// Define vuelidate object.
const v$ = useVuelidate(rules, formState)

// Perform vuelidate validation when mounted.
onMounted(() => {
  v$.value.$touch()
})

// Define the exposed properties.
defineExpose({
  v$, // parent component's vuelidate picks this up
})
</script>

<template>
  <div
    v-if="props.showFiltrationInlineHelp"
    class="alert alert-secondary small p-2 m-2"
  >
    <i-mdi-information />

    Adjust the settings in this tab to configure the annotation with TAD
    information.
  </div>
  <div class="form-inline p-2">
    <label for="tadSetInput"> TAD Set </label>
    <div class="input-group input-group-sm ml-2 mr-4">
      <select
        v-model="v$.tad_set.$model"
        class="custom-select custom-select-sm"
      >
        <option value="hesc">hESC TADs (Dixon et al., 2019)</option>
        <option value="imr90">IMR90 TADs (Dixon et al., 2019)</option>
      </select>
    </div>
  </div>
  <div v-if="filtrationComplexityMode == 'dev'" class="card-footer">
    <span class="text-nowrap">
      <i-mdi-account-hard-hat />
      <strong class="pl-2">Developer Info:</strong>
    </span>
    <code>
      {{ dumpTads() }}
    </code>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
