<script setup>
import { useVuelidate } from '@vuelidate/core'
import { maxValue, minValue, numeric } from '@vuelidate/validators'
import { computed, onMounted } from 'vue'

// Define the component's props.
const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  querySettings: Object,
})

// The keys of the settings for this tab.
const settingsKeys = ['clinvar_sv_min_overlap', 'clinvar_sv_min_pathogenicity']

// Return JSON string with settings from this tab to be displayed in "dev" mode.
const dumpPathoInfo = () => {
  const result = {}
  for (const [key, value] of Object.entries(props.querySettings)) {
    if (settingsKeys.includes(key)) {
      result[key] = value
    }
  }
  return JSON.stringify(result)
}

// Define validation rules.
const rules = {
  clinvar_sv_min_overlap: {
    numeric,
    minValue: minValue(0.0),
    maxValue: maxValue(1.0),
    $autoDirty: true,
  },
  clinvar_sv_min_pathogenicity: {
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
  ..._vuelidateWrappers(settingsKeys),
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
  <div class="form-group p-2">
    <label for="clinvarMinOverlap"> ClinVar SV min. overlap </label>
    <div class="input-group input-group-sm">
      <input
        id="clinvarMinOverlap"
        v-model.trim.lazy="v$.clinvar_sv_min_overlap.$model"
        placeholder="Min. SV overlap with ClinVar SVs"
        class="form-control"
        :class="{
          'is-invalid': v$.clinvar_sv_min_overlap.$error,
        }"
      />
      <div
        v-for="error of v$.clinvar_sv_min_overlap.$errors"
        :key="error.$uid"
        class="invalid-feedback"
      >
        {{ error.$message }}
      </div>
    </div>
  </div>

  <div class="form-group p-2">
    <label for="clinvarMinPathogenicity"> ClinVar SV min. pathogenicity </label>
    <div class="input-group input-group-sm">
      <select
        id="clinvarMinPathogenicity"
        v-model="v$.clinvar_sv_min_pathogenicity.$model"
        class="custom-select custom-select-sm"
      >
        <option value="benign">Benign</option>
        <option value="likely-benign">Likely benign</option>
        <option value="uncertain">Uncertain</option>
        <option value="likely-pathogenic">Likely pathogenic</option>
        <option value="pathogenic">Pathogenic</option>
      </select>
    </div>
  </div>
  <div v-if="filtrationComplexityMode == 'dev'" class="card-footer">
    <span class="text-nowrap">
      <i-mdi-account-hard-hat />
      <strong class="pl-2">Developer Info:</strong>
    </span>
    <code>
      {{ dumpPathoInfo() }}
    </code>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
