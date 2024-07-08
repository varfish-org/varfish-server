<script setup>
import Multiselect from '@vueform/multiselect'
import {
  DisplayFrequencies,
  DisplayConstraints,
  DisplayColumns,
  DisplayDetails,
} from '@/variants/enums'
import { computed } from 'vue'

const props = defineProps({
  // model props
  displayDetails: Number,
  displayFrequency: Number,
  displayConstraint: Number,
  displayColumns: Array,
  // the defined extra anno fields
  extraAnnoFields: Array,
})

const emit = defineEmits([
  'update:displayDetails',
  'update:displayFrequency',
  'update:displayConstraint',
  'update:displayColumns',
])

// The static column options.
const staticColumnOptions = Object.values(DisplayColumns).map(
  ({ value, text }) => {
    return {
      value: value,
      label: text,
    }
  },
)

// The columns for extra_annos.
const extraColumnOptions = (props.extraAnnoFields ?? []).map(
  ({ field, label }) => ({
    value: `extra_anno${field}`,
    label: label,
  }),
)

// Concatenate to column options.
const columnOptions = staticColumnOptions.concat(extraColumnOptions)

const displayDetailsWrapper = computed({
  get() {
    return props.displayDetails
  },
  set(newValue) {
    emit('update:displayDetails', newValue)
  },
})

const displayFrequencyWrapper = computed({
  get() {
    return props.displayFrequency
  },
  set(newValue) {
    emit('update:displayFrequency', newValue)
  },
})

const displayConstraintWrapper = computed({
  get() {
    return props.displayConstraint
  },
  set(newValue) {
    emit('update:displayConstraint', newValue)
  },
})

const displayColumnsWrapper = computed({
  get() {
    return props.displayColumns || []
  },
  set(newValue) {
    emit('update:displayColumns', newValue)
  },
})
</script>

<template>
  <div class="pr-3 align-self-start">
    <div>
      <label class="font-weight-bold small mb-0 text-nowrap">
        Coordinates / ClinVar
      </label>
    </div>
    <select
      v-model="displayDetailsWrapper"
      class="custom-select custom-select-sm"
      style="width: 150px"
    >
      <option
        v-for="option in DisplayDetails"
        :key="option"
        :value="option.value"
      >
        {{ option.text }}
      </option>
    </select>
  </div>

  <div class="pr-3 align-self-start">
    <div>
      <label class="font-weight-bold small mb-0 text-nowrap">
        Frequency & #Hom
      </label>
    </div>
    <select
      v-model="displayFrequencyWrapper"
      class="custom-select custom-select-sm"
      style="width: 150px"
    >
      <option
        v-for="option in DisplayFrequencies"
        :key="option"
        :value="option.value"
      >
        {{ option.text }}
      </option>
    </select>
  </div>

  <div class="pr-3 align-self-start">
    <div>
      <label class="font-weight-bold small mb-0 text-nowrap">
        Constraints
      </label>
    </div>
    <select
      v-model="displayConstraintWrapper"
      class="custom-select custom-select-sm"
      style="width: 150px"
    >
      <option
        v-for="option in DisplayConstraints"
        :key="option"
        :value="option.value"
      >
        {{ option.text }}
      </option>
    </select>
  </div>

  <div class="pr-3 align-self-start extra-columns">
    <div style="width: 250px">
      <label class="font-weight-bold small mb-0 text-nowrap">
        Extra Columns
      </label>
    </div>
    <Multiselect
      v-model="displayColumnsWrapper"
      mode="multiple"
      :hide-selected="false"
      :allow-empty="true"
      :close-on-select="true"
      :searchable="true"
      :options="columnOptions"
    />
  </div>
</template>

<style src="@vueform/multiselect/themes/default.css"></style>

<style>
.extra-columns {
  --ms-font-size: 0.875rem;
  --ms-line-height: 1.5;
  --ms-py: 0.26rem;
  --ms-caret-color: #343a40;
  --ms-clear-color: #343a40;
}

.multiselect {
  color: #343a40;
}
</style>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
