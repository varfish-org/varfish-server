<script setup>
import Multiselect from '@vueform/multiselect'
import { onMounted, ref, watch } from 'vue'

import {
  hpoInheritance,
  hpoAgeOfOnset,
} from '@variants/components/HpoTermInput.values'
import { declareWrapper } from '@variants/helpers'

const props = defineProps({
  apiEndpoint: {
    type: String,
    default: '/variants/ajax/hpo-terms/',
  },
  csrfToken: String,
  showFiltrationInlineHelp: Boolean,
  modelValue: {
    type: Array,
    default: () => [],
  },
  id: String,
  showHpoShortcutsButton: Boolean,
})

const emit = defineEmits(['update:modelValue'])

/** The model value that we are handling. */
const value = declareWrapper(props, 'modelValue', emit)

/** The text value that we are presenting to the user. */
const textValue = ref(null)

/** Whether the Multiselect is loading from server. */
const loading = ref(false)

const fetchHpoTerms = async (query) => {
  const queryArg = encodeURIComponent(query)
  const response = await fetch(`${props.apiEndpoint}?query=${queryArg}`, {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    'X-CSRFToken': props.csrfToken,
  })
  const results = await response.json()
  const data = results.map(({ id, name }) => {
    return {
      label: `${id} - ${name}`,
      value: {
        term_id: id,
        name,
      },
    }
  })

  return data
}

const fetchHpoTermsForMultiselect = async (query) => {
  loading.value = true
  const result = await fetchHpoTerms(query)
  loading.value = false
  return result
}

/** Refresh text value from terms. */
const refreshTextValue = async (termsArray) => {
  const withLabelUnfiltered = await Promise.all(
    termsArray.map(async (hpoTerm) => {
      const fetched = await fetchHpoTerms(hpoTerm)
      if (fetched && fetched.length > 0) {
        return fetched[0].label
      } else {
        return null
      }
    }),
  )
  const withLabel = withLabelUnfiltered.filter((elem) => elem !== null)
  textValue.value = withLabel.join('; ')
}

/** Refresh model value from text value. */
const refreshModelValue = () => {
  const regex = /(HP:\d{7}|OMIM:\d{6}|DECIPHER:\d+|ORPHA:\d+)( - [^;]+)?(;|$)/g
  const cleanTextValue = (textValue.value || '')
    .replace(/^\s*;?\s*|\s*;?\s*$/g, '') // replace any cruft in beginning or end of the string
    .replace(/\s{2,}/g, ' ') // replace double (or more) spaces with one space
    .replace(/[;\s]{2,}/g, '; ') // replace any sequence of multiple ; and spaces with `; `
    .replace(/;([^\s$])/g, '; $1') // add missing space after semicolon
    .replace(/([^;])\s(HP|OMIM|DECIPHER|ORPHA):/g, '$1; $2:') // set missing semicolons in front of HPO id
  const hpoSelected = []
  let result
  while ((result = regex.exec(cleanTextValue))) {
    if (!hpoSelected.includes(result[1])) {
      hpoSelected.push(result[1])
    }
  }
  value.value = hpoSelected
  refreshTextValue(hpoSelected)
}

/** Push term to field. */
const appendHpoTerm = async (term) => {
  value.value.push(term)
  refreshTextValue(value.value)
}

const refreshing = ref(false)

const manuallyRefreshModelValue = () => {
  refreshing.value = true
  refreshModelValue()
  refreshing.value = false
}

const hpoTermSelected = (item) => {
  if (!item) {
    return
  }

  let newValue = ''
  if (textValue.value && textValue.value.trim().length !== 0) {
    newValue = textValue.value.trim() + '; '
  }
  newValue += `${item.value.term_id} - ${item.value.name}`

  textValue.value = newValue

  refreshModelValue()
}

const debugTerms = ref(false)

const showHpoShortcuts = ref(false)

watch(
  () => props.modelValue,
  (newValue, _oldValue) => {
    refreshTextValue(newValue)
  },
)

onMounted(() => {
  if (props.modelValue) {
    refreshTextValue(props.modelValue)
  }
})
</script>

<template>
  <div>
    <div class="input-group mb-3">
      <textarea
        :id="id"
        v-model="textValue"
        class="form-control"
        rows="3"
      ></textarea>
      <div class="input-group-append">
        <span
          class="input-group-text refresh-button"
          @click="manuallyRefreshModelValue()"
          title="Verify and clean terms from text input"
        >
          <i-mdi-refresh :class="{ spin: refreshing }" />
        </span>
      </div>
    </div>
    <code v-if="debugTerms">{{ props.modelValue }}</code>
    <div
      v-if="props.showFiltrationInlineHelp"
      class="alert alert-secondary small p-2"
    >
      <i-mdi-information />
      Type into the box below to search for HPO/OMIM/Decipher terms. Select
      terms to add them to the text box above. You can also just type the terms
      into the text box above. To remove terms, just remove them from the text
      box.
    </div>
    <div class="row ml-0 mr-0">
      <Multiselect
        class="col"
        mode="single"
        placeholder="HPO Term Lookup"
        no-options-text="Type to start searching"
        :filter-results="false"
        :allow-empty="true"
        :close-on-select="true"
        :searchable="true"
        :object="true"
        :resolve-on-load="false"
        :loading="loading"
        :delay="1"
        :min-chars="3"
        :options="fetchHpoTermsForMultiselect"
        @change="hpoTermSelected"
      />
      <button
        v-if="showHpoShortcutsButton"
        type="button"
        class="btn btn-secondary col-auto ml-2 text-white"
        title="HPO term shortcuts"
        @click="showHpoShortcuts = !showHpoShortcuts"
      >
        <i-mdi-dots-horizontal />
      </button>
    </div>
    <div v-if="showHpoShortcuts" class="row">
      <div class="col pl-0 pr-0 small">
        <h6 class="mt-2" style="font-size: 1.2em">Inheritance</h6>
        <template v-for="(item, index) in hpoInheritance">
          <span class="pl-1 pr-1" v-if="index > 0">&middot;</span>
          <a href="#" @click.prevent="appendHpoTerm(item.term)">{{
            item.label
          }}</a>
        </template>
        <h6 class="mt-2" style="font-size: 1.2em">Age of Onset</h6>
        <template v-for="(item, index) in hpoAgeOfOnset">
          <span class="pl-1 pr-1" v-if="index > 0">&middot;</span>
          <a href="#" @click.prevent="appendHpoTerm(item.term)">{{
            item.label
          }}</a>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.refresh-button {
  cursor: pointer;
}

.refresh-button:hover {
  color: #fff;
  background-color: #5a6268;
  border-color: #545b62;
}

.spin {
  animation-name: spin-anim;
  animation-duration: 2500ms;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}

@keyframes spin-anim {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

<style src="@vueform/multiselect/themes/default.css"></style>
