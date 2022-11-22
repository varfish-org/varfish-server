<script setup>
import { computed, onMounted } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { integer, minValue } from '@vuelidate/validators'

import {
  svSubTypeGroups,
  svTypeGroups,
  svSubTypeFields,
} from './SvFilterFormImpactPane.fields.js'

// Define the component's props.
const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  querySettings: Object,
})

// Return JSON string with settings from this tab to be displayed in "dev" mode.
const dumpSvTypes = () => {
  const result = {}
  for (const [key, value] of Object.entries(props.querySettings)) {
    if (
      ['sv_size_min', 'sv_size_max', 'sv_types', 'sv_sub_types'].includes(key)
    ) {
      result[key] = value
    }
  }
  return JSON.stringify(result)
}

// Define validation rules.
const rules = {
  sv_size_min: {
    integer,
    minValue: minValue(0),
    $autoDirty: true,
  },
  sv_size_max: {
    integer,
    minValue: minValue(0),
    $autoDirty: true,
  },
}

// Helper function to build wrappers that catch the case of props.querySettings not being set.
// This is used for the atomic value wrappers.
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
    ])
  )

// Helper function to build wrappers for array valued fields.
const buildSvSubTypeWrapper = (key) => {
  return computed({
    get() {
      if (!props.querySettings.sv_sub_types) {
        return false
      } else {
        return props.querySettings.sv_sub_types.includes(key)
      }
    },
    set(newValue) {
      if (props.querySettings.effects) {
        const isSet = props.querySettings.sv_sub_types.includes(key)
        if (newValue && !isSet) {
          props.querySettings.sv_sub_types.push(key)
        } else if (!newValue && isSet) {
          props.querySettings.sv_sub_types =
            props.querySettings.sv_sub_types.filter((val) => val !== key)
        }
      }
    },
  })
}

// Build wrappers for SV subtypes.
const svSubTypeWrappers = {}
for (const group of svSubTypeGroups) {
  for (const field of group.fields) {
    svSubTypeWrappers[field.id] = buildSvSubTypeWrapper(field.id)
  }
}

const buildSvTypeGroupWrapper = (key) => {
  return computed({
    get() {
      const currentSvSubTypes = new Set(props.querySettings.sv_sub_types)
      const allSet = svTypeGroups[key].every((value) =>
        currentSvSubTypes.has(value)
      )
      return allSet
    },
    set(groupValue) {
      const newSvSubTypes = new Set(props.querySettings.sv_sub_types)
      for (const effect of svTypeGroups[key]) {
        if (groupValue) {
          newSvSubTypes.add(effect)
        } else {
          newSvSubTypes.delete(effect)
        }
      }
      props.querySettings.sv_sub_types = Array.from(newSvSubTypes).sort()
    },
  })
}
const svTypeGroupWrappers = {}
for (const name of Object.keys(svTypeGroups)) {
  svTypeGroupWrappers[name] = buildSvTypeGroupWrapper(name)
}

const buildSvTypeGroupIndeterminate = (key) => {
  return computed(() => {
    const currentSvSubTypes = new Set(props.querySettings.sv_sub_types)
    const allSet = svTypeGroups[key].every((value) =>
      currentSvSubTypes.has(value)
    )
    const noneSet = svTypeGroups[key].every(
      (value) => !currentSvSubTypes.has(value)
    )
    return !allSet && !noneSet
  })
}

const svTypeGroupIndeterminates = {}
for (const name of Object.keys(svTypeGroups)) {
  svTypeGroupIndeterminates[name] = buildSvTypeGroupIndeterminate(name)
}

// Define the form state.
const formState = {
  ..._vuelidateWrappers(['sv_size_min', 'sv_size_max']),
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
  <div style="position: relative" class="mr-2 mt-2">
    <div
      v-if="props.showFiltrationInlineHelp"
      class="alert alert-secondary small p-2 m-2 mb-0"
    >
      <i-mdi-information />
      This panel allows to fine-tune the filtration of variants based on the
      predicted molecular impact. In most cases, using the quick presets will be
      enough.
      <strong>
        This (quite complex) part of the filtration form is only intended for
        advanced/experienced users.
      </strong>
    </div>

    <!-- Row 1: Minimal and Maximal SV Size -->
    <div class="row">
      <div class="col mt-2 mb-2">
        <h5>SV Size</h5>
        <div
          v-if="props.showFiltrationInlineHelp"
          class="alert alert-secondary small mt-2 p-2 mb-2"
        >
          <i-mdi-information />
          Define an optional lower and upper limit of the SVs to return. This
          setting does not apply to break-ends (BNDs).
        </div>
        <div class="form-inline">
          <label for="minSvSize">Min. SV size</label>
          <div class="input-group input-group-sm ml-2 mr-4">
            <input
              id="minSvSize"
              type="text"
              class="form-control"
              placeholder="min. SV size"
              v-model.trim.lazy="v$.sv_size_min.$model"
              :class="{
                'is-invalid': v$.sv_size_min.$error,
              }"
            />
            <div class="input-group-append">
              <span class="input-group-text">bp</span>
            </div>
            <div
              v-for="error of v$.sv_size_min.$errors"
              :key="error.$uid"
              class="invalid-feedback"
            >
              {{ error.$message }}
            </div>
          </div>

          <label for="maxSvSize">Max. SV size</label>
          <div class="input-group input-group-sm ml-2">
            <input
              id="maxSvSize"
              type="text"
              class="form-control"
              placeholder="max. SV size"
              v-model.trim.lazy="v$.sv_size_max.$model"
              :class="{
                'is-invalid': v$.sv_size_max.$error,
              }"
            />
            <div class="input-group-append">
              <span class="input-group-text">bp</span>
            </div>
            <div
              v-for="error of v$.sv_size_max.$errors"
              :key="error.$uid"
              class="invalid-feedback"
            >
              {{ error.$message }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Row 2: SV Type -->
    <div class="row border-top mt-2">
      <div class="col mt-2 mb-2">
        <h5>SV Types</h5>
        <div
          v-if="props.showFiltrationInlineHelp"
          class="alert alert-secondary small mt-2 p-2 mb-2"
        >
          <i-mdi-information />
          Limit the resulting SVs to certain types.
        </div>
        <div
          v-for="field in svSubTypeFields"
          class="custom-control custom-checkbox custom-control-inline"
        >
          <input
            :id="`sv-type-${field.id}`"
            type="checkbox"
            class="custom-control-input"
            :indeterminate.prop="svTypeGroupIndeterminates[field.id].value"
            v-model="svTypeGroupWrappers[field.id].value"
          />
          <label class="custom-control-label" :for="`sv-type-${field.id}`">
            {{ field.label }}
          </label>
        </div>
      </div>
    </div>

    <!-- Row 3: SV Sub Types -->
    <div class="row border-top mt-2">
      <div class="col mt-2 mb-2">
        <h5>SV Sub Types</h5>
        <div class="row">
          <div class="pl-0 col" v-for="group in svSubTypeGroups">
            <strong>{{ group.title }}</strong>
            <br />
            <div
              v-for="field in group.fields"
              class="custom-control custom-checkbox custom-control-inline"
              title="${field.explanation}"
            >
              <input
                :id="`sv-sub-type-${field.id}`"
                type="checkbox"
                class="custom-control-input"
                v-model="svSubTypeWrappers[field.id].value"
              />
              <label
                class="custom-control-label"
                :for="`sv-sub-type-${field.id}`"
              >
                {{ field.label }}
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-if="filtrationComplexityMode == 'dev'" class="card-footer">
    <span class="text-nowrap">
      <i-mdi-account-hard-hat />
      <strong class="pl-2">Developer Info:</strong>
    </span>
    <code>
      {{ dumpSvTypes() }}
    </code>
  </div>
</template>
