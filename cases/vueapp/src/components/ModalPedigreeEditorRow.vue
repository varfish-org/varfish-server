<script setup>
/**
 * Helper component as a row in `ModalPedigreeEditor`.
 */
import { useVuelidate } from '@vuelidate/core'
import { helpers } from '@vuelidate/validators'
import { onMounted, computed } from 'vue'
import { displayName } from '@varfish/helpers.js'

/** Define the props. */
const props = defineProps({
  pedigree: Array,
  name: String,
  father: String,
  mother: String,
  sex: Number,
  affected: Number,
})

/** Define emits. */
const emit = defineEmits([
  'update:father',
  'update:mother',
  'update:sex',
  'update:affected',
])

/** Construct wrapper for props to be used in formState. */
const createWrapper = (key) =>
  computed({
    get() {
      return props[key]
    },
    set(newValue) {
      emit(`update:${key}`, newValue)
    },
  })

/** Extract names from props.pedigree. */
const names = computed(() => {
  return props.pedigree.map((line) => line.name)
})

/** The state to use in vuelidate. */
const formState = {
  father: createWrapper('father'),
  mother: createWrapper('mother'),
  sex: createWrapper('sex'),
  affected: createWrapper('affected'),
}

/** The names of male individuals. */
const males = computed(() =>
  props.pedigree.filter((entry) => entry.sex === 1).map((entry) => entry.name)
)
const females = computed(() =>
  props.pedigree.filter((entry) => entry.sex === 2).map((entry) => entry.name)
)

/** Custom validators. */
const selfCannotBeParent = helpers.withMessage(
  'Cannot be their own parent',
  (value) => value !== props.name
)
const fatherSexFits = helpers.withMessage(
  `Sex of father must be male`,
  (value) => value === '0' || males.value.includes(value)
)
const motherSexFits = helpers.withMessage(
  `Sex of mother must be female`,
  (value) => value === '0' || females.value.includes(value)
)

/** Single-row validation roles. */
const rules = {
  father: [selfCannotBeParent, fatherSexFits],
  mother: [selfCannotBeParent, motherSexFits],
  sex: [],
  affected: [],
}

const v$ = useVuelidate(rules, formState)

/** Initialize form value and vuelidate. */
onMounted(() => {
  v$.value.$touch()
})

/** Define exposed values. */
defineExpose({ v$ })
</script>

<template>
  <tr>
    <td class="text-nowrap">
      {{ displayName(name) }}
    </td>
    <td>
      <select
        class="custom-select custom-select-sm"
        v-model="v$.father.$model"
        :class="{
          // 'is-valid': !v$.father.$error,
          'is-invalid': v$.father.$error,
        }"
      >
        <option value="0">0 (founder)</option>
        <option v-for="name in names" :value="name">
          {{ displayName(name) }}
        </option>
      </select>
      <div
        v-for="error of v$.father.$errors"
        :key="error.$uid"
        class="invalid-feedback"
      >
        {{ error.$message }}
      </div>
    </td>
    <td>
      <select
        class="custom-select custom-select-sm"
        v-model="v$.mother.$model"
        :class="{
          // 'is-valid': !v$.mother.$error,
          'is-invalid': v$.mother.$error,
        }"
      >
        <option value="0">0 (founder)</option>
        <option v-for="name in names" :value="name">
          {{ displayName(name) }}
        </option>
      </select>
      <div
        v-for="error of v$.mother.$errors"
        :key="error.$uid"
        class="invalid-feedback"
      >
        {{ error.$message }}
      </div>
    </td>
    <td>
      <select
        class="custom-select custom-select-sm"
        v-model="v$.sex.$model"
        :class="{
          // 'is-valid': !v$.sex.$error,
          'is-invalid': v$.sex.$error,
        }"
      >
        <option :value="0">unknown</option>
        <option :value="1">male</option>
        <option :value="2">female</option>
      </select>
      <div
        v-for="error of v$.sex.$errors"
        :key="error.$uid"
        class="invalid-feedback"
      >
        {{ error.$message }}
      </div>
    </td>
    <td>
      <select
        class="custom-select custom-select-sm"
        v-model="v$.affected.$model"
        :class="{
          // 'is-valid': !v$.affected.$error,
          'is-invalid': v$.affected.$error,
        }"
      >
        <option :value="0">unknown</option>
        <option :value="1">unaffected</option>
        <option :value="2">affected</option>
      </select>
      <div
        v-for="error of v$.affected.$errors"
        :key="error.$uid"
        class="invalid-feedback"
      >
        {{ error.$message }}
      </div>
    </td>
  </tr>
</template>
