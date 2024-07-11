<script setup>
import { computed, onMounted } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { integer, minValue } from '@vuelidate/validators'

// Define the component's props.
const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  querySettings: Object,
})

// Return JSON string with settings from this tab to be displayed in "dev" mode.
const dumpRegulatory = () => {
  const result = {}
  for (const [key, value] of Object.entries(props.querySettings)) {
    if ([].includes(key)) {
      result[key] = value
    }
  }
  return JSON.stringify(result)
}

// Define validation rules.
const rules = {
  regulatory_general_padding: {
    integer,
    minValue: minValue(0),
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
  ..._vuelidateWrappers(['regulatory_general_padding']),
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

    Adjust the settings in this tab to configure the annotation with built-in
    and user-defined regulatory elements VarFish instance.
  </div>
  <div class="form-inline p-2">
    <label for="regulatoryGeneralPaddingInput">
      Allowed distance/padding
    </label>
    <div class="input-group input-group-sm ml-2 mr-4">
      <input
        id="regulatoryGeneralPaddingInput"
        v-model.trim.lazy="v$.regulatory_general_padding.$model"
        type="text"
        class="form-control"
        placeholder="allowed distance"
        :class="{
          'is-invalid': v$.regulatory_general_padding.$error,
        }"
      />
      <div class="input-group-append">
        <span class="input-group-text">bp</span>
      </div>
      <div
        v-for="error of v$.regulatory_general_padding.$errors"
        :key="error.$uid"
        class="invalid-feedback"
      >
        {{ error.$message }}
      </div>
    </div>
  </div>
  <div class="p-2">
    <h5>
      Custom Regulatory Maps
      <span class="text-muted small">(Installed by Instance Admin)</span>
    </h5>
  </div>
  <div v-if="filtrationComplexityMode == 'dev'" class="card-footer">
    <span class="text-nowrap">
      <i-mdi-account-hard-hat />
      <strong class="pl-2">Developer Info:</strong>
    </span>
    <code>
      {{ dumpRegulatory() }}
    </code>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
