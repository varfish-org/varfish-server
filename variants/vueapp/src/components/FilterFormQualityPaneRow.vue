<script setup>
import { declareWrapper } from '../helpers.js'
import { displayName } from '@varfish/helpers.js'
import { onMounted } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import {
  numericKeys,
  failValues,
  rules,
  allKeys,
} from './FilterFormQualityPane.values.js'

const props = defineProps({
  index: Number,
  caseName: String,
  member: Object,
  qualMinDpHet: Number,
  qualMinDpHom: Number,
  qualMinAb: Number,
  qualMinGq: Number,
  qualMinAd: Number,
  qualMaxAd: Number,
  qualFail: String,
})

const emit = defineEmits([
  'update:qualMinDpHet',
  'update:qualMinDpHom',
  'update:qualMinAb',
  'update:qualMinGq',
  'update:qualMinAd',
  'update:qualMaxAd',
  'update:qualFail',
])

const mappers = {
  qualMinDpHet: parseInt,
  qualMinDpHom: parseInt,
  qualMinAb: parseFloat,
  qualMinGq: parseInt,
  qualMinAd: parseInt,
  qualMaxAd: parseInt,
}

const formModel = Object.fromEntries(
  allKeys.map((key) => [
    key,
    declareWrapper(props, key, emit, mappers[key], key !== 'qualFail'),
  ])
)

const v$ = useVuelidate(rules, formModel)

/**
 * @return {boolean} whether the form is currently valid or not
 */
const isValid = () => {
  return !v$.invalid
}

onMounted(() => {
  v$.value.$touch()
})

defineExpose({ isValid })
</script>

<template>
  <tr>
    <td>{{ index }}</td>
    <td>{{ caseName }}</td>
    <td>{{ displayName(member.name) }}</td>
    <td>{{ displayName(member.father) }}</td>
    <td>{{ displayName(member.mother) }}</td>
    <td v-for="key in numericKeys">
      <input
        type="text"
        v-model="v$[key].$model"
        class="form-control form-control-sm"
        :class="{
          // 'is-valid': !v$[key].$error,
          'is-invalid': v$[key].$error,
        }"
      />
      <div
        v-for="error of v$[key].$errors"
        :key="error.$uid"
        class="invalid-feedback"
      >
        {{ error.$message }}
      </div>
    </td>
    <td>
      <select
        v-model="v$.qualFail.$model"
        :class="{
          // 'is-valid': !v$.qualFail.$error,
          'is-invalid': v$.qualFail.$error,
        }"
        class="custom-select custom-select-sm"
      >
        <option v-for="(label, value) in failValues" :value="value">
          {{ label }}
        </option>
      </select>
    </td>
  </tr>
</template>
