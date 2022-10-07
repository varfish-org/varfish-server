<script setup>
import Multiselect from '@vueform/multiselect'
import { useVuelidate } from '@vuelidate/core'
import { helpers, numeric, required } from '@vuelidate/validators'
import { computed, onMounted, ref } from 'vue'

import clinvarExportApi from '@clinvarexport/api/clinvarExport'
import {
  useClinvarExportStore,
  VARIANT_ZYGOSITY_OPTIONS,
  VARIANT_ORIGIN_OPTIONS,
  SAMPLE_SOURCE_OPTIONS,
} from '@clinvarexport/stores/clinvar-export'

const components = { Multiselect }

// Define props and emits and related writeable computed propery
const props = defineProps(['modelValue'])
const emit = defineEmits(['update:modelValue'])
const value = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  },
})

const getIndividualName = () => {
  if (value.value) {
    const submissionIndividual =
      store.submissionIndividuals[value.value.sodar_uuid]
    return store.individuals[submissionIndividual.individual].name
      .replace('-N1-DNA1-WES1', '')
      .replace('-N1-DNA1-WGS1', '')
  } else {
    return null
  }
}

// Define Pinia store
const store = useClinvarExportStore()

// Local state used for loading HPO terms
const hpoTermsLoading = ref(false)

// Helper function to build wrappers that set the values via the store
function _vuelidateWrappers(keys) {
  return Object.fromEntries(
    keys.map((key) => [
      key,
      computed({
        get() {
          if (!value.value) {
            return null
          }
          return store.submissionIndividuals[value.value.sodar_uuid][key]
        },
        set(newValue) {
          if (!value.value.sodar_uuid) {
            return
          }
          const submissionIndividual =
            store.submissionIndividuals[value.value.sodar_uuid]
          submissionIndividual[key] = newValue
        },
      }),
    ])
  )
}

// Define object with the data to edit in the form.  We construct custom wrappers so we can easily pass this into vuelidate.
const formState = {
  ..._vuelidateWrappers([
    'source',
    'tissue',
    'variant_origin',
    'variant_allele_count',
    'variant_zygosity',
  ]),
  phenotypes: computed({
    get() {
      if (!value.value || !value.value.sodar_uuid) {
        return []
      } else {
        return store.submissionIndividuals[
          value.value.sodar_uuid
        ].phenotypes.map((obj) => {
          return {
            value: obj,
            label: `${obj.term_id} -- ${obj.term_name}`,
          }
        })
      }
    },
    set(newValue) {
      if (!value.value || !value.value.sodar_uuid) {
        return
      } else {
        store.updateSubmissionIndividual({
          submissionIndividual: value.value,
          key: 'phenotypes',
          value: newValue.map((v) => v.value),
        })
      }
    },
  }),
  citations: computed({
    get() {
      if (!value.value) {
        return ''
      }
      const submissionIndividual =
        store.submissionIndividuals[value.value.sodar_uuid]
      return submissionIndividual.citations.join(' ')
    },
    set(newValue) {
      const submissionIndividual =
        store.submissionIndividuals[value.value.sodar_uuid]
      store.updateSubmissionIndividual({
        submissionIndividual,
        key: 'citations',
        value: newValue.split(/[ ,]+/),
      })
    },
  }),
}

// Define validation rules.
const rules = {
  phenotypes: {},
  variant_allele_count: {
    required,
    numeric,
  },
  variant_zygosity: {
    isValidChoice: (x) => VARIANT_ZYGOSITY_OPTIONS.includes(x),
  },
  variant_origin: {
    required,
    isValidChoice: (x) => VARIANT_ORIGIN_OPTIONS.includes(x),
  },
  source: {
    required,
    isValidChoice: (x) => SAMPLE_SOURCE_OPTIONS.includes(x),
  },
  tissue: {
    required,
  },
  citations: {
    isValidChoice: (pmids) =>
      !helpers.req(pmids) ||
      pmids.split(/[ ,]+/).every((s) => s.match(/^PMID:\d+$/)),
  },
}

// Define vuelidate object
const v$ = useVuelidate(rules, formState)

const mounted = () => {
  v$.$touch()
}

/**
 * @param up whether to consider up movement (false is down)
 * @return {boolean} whether moving into the given direction is currently disabled
 */
const isMoveDisabled = (up) => {
  if (!props.modelValue) {
    return true
  }
  const other = props.modelValue.sort_order + (up ? -1 : 1)
  return (
    other < 0 || other >= store.currentSubmission.submission_individuals.length
  )
}

/**
 * Find HPO term matching the `query` nad set into appropriate local stae.
 *
 * @param query The query string to search for.
 */
const asyncFindHpoTerms = async (query) => {
  hpoTermsLoading.value = true
  const response = await clinvarExportApi.queryHpo(store.appContext, query)
  const result = response.result.map((obj) => {
    return {
      value: obj,
      label: `${obj.term_id} -- ${obj.term_name}`,
    }
  })
  hpoTermsLoading.value = false
  return result
}

/**
 * @return {boolean} whether the form is currently valid or not
 */
const isValid = () => {
  return !v$.$invalid
}

onMounted(() => {
  v$.value.$touch()
})

// Define the exposed functions
defineExpose({
  isValid,
  // for testing
  hpoTermsLoading,
  isMoveDisabled,
  store,
})
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h4 class="mb-0 ml-0">
        Case &raquo;{{ getIndividualName() }}&laquo;
        <div class="btn-group float-right pb-0 mb-0">
          <button
            type="button"
            class="btn btn-sm btn-secondary"
            :disabled="isMoveDisabled(true)"
            @click="
              store.moveSubmissionIndividual({
                submissionIndividual: value,
                up: true,
              })
            "
          >
            <i class="iconify" data-icon="mdi:arrow-up-circle"></i>
            move up
          </button>
          <button
            type="button"
            class="btn btn-sm btn-secondary"
            :disabled="isMoveDisabled(false)"
            @click="
              store.moveSubmissionIndividual({
                submissionIndividual: value,
                up: false,
              })
            "
          >
            <i class="iconify" data-icon="mdi:arrow-down-circle"></i>
            move down
          </button>
          <button
            type="button"
            class="btn btn-sm btn-danger"
            @click="
              store.removeSubmissionIndividualFromCurrentSubmission(value)
            "
          >
            <span
              class="iconify"
              data-icon="mdi:close"
              data-inline="false"
            ></span>
            remove from variant
          </button>
        </div>
      </h4>
    </div>
    <div class="card-body px-2">
      <div class="row">
        <div class="col-12 px-0">
          <div id="input-group-phenotypes" class="form-group">
            <label for="input-phenotypes">Phenotype HPO Terms</label>
            <multiselect
              id="input-phenotypes"
              v-model="v$.phenotypes.$model"
              placeholder="Add HPO terms for this individual"
              mode="tags"
              :filter-results="false"
              :allow-empty="true"
              :close-on-select="true"
              :searchable="true"
              :object="true"
              :resolve-on-load="false"
              :loading="hpoTermsLoading"
              :delay="1"
              :min-chars="2"
              style="white-space: nowrap"
              :class="{
                'is-valid': !v$.phenotypes.$error,
                'is-invalid': v$.phenotypes.$error,
              }"
              :options="asyncFindHpoTerms"
            ></multiselect>
            <small class="form-text text-muted">
              Add any HPO terms that are present in the individual.
            </small>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-4 pl-0">
          <div id="input-group-source" class="form-group">
            <label for="input-source">Sample Source</label>
            <select
              id="input-source"
              v-model="v$.source.$model"
              required
              :class="{
                'custom-select is-valid': !v$.source.$error,
                'custom-select is-invalid': v$.source.$error,
              }"
            >
              <option>Chose...</option>
              <option
                v-for="sampleSourceOption in SAMPLE_SOURCE_OPTIONS"
                :key="sampleSourceOption"
                :value="sampleSourceOption"
              >
                {{ sampleSourceOption }}
              </option>
            </select>
            <div
              v-for="error of v$.source.$errors"
              :key="error.$uid"
              class="invalid-feedback"
            >
              {{ error.$message }}
            </div>
          </div>
        </div>
        <div class="col-4">
          <div id="input-group-tissue" class="form-group">
            <label for="input-source">Tissue</label>
            <input
              id="input-tissue"
              v-model="v$.tissue.$model"
              required
              :class="{
                'form-control is-valid': !v$.tissue.$error,
                'form-control is-invalid': v$.tissue.$error,
              }"
            />
            <div
              v-for="error of v$.tissue.$errors"
              :key="error.$uid"
              class="invalid-feedback"
            >
              {{ error.$message }}
            </div>
          </div>
        </div>
        <div class="col-4 pr-0">
          <div id="input-group-citations" class="form-group">
            <label for="input-citations">Citations</label>
            <input
              id="input-citations"
              v-model.trim="v$.citations.$model"
              required
              :class="{
                'form-control is-valid': !v$.citations.$error,
                'form-control is-invalid': v$.citations.$error,
              }"
            />
            <div
              v-for="error of v$.citations.$errors"
              :key="error.$uid"
              class="invalid-feedback"
            >
              {{ error.$message }}
            </div>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-4 pl-0">
          <div id="input-group-variant-origin" class="form-group">
            <label for="input-source">Variant Origin</label>
            <select
              id="input-variant-origin"
              v-model="v$.variant_origin.$model"
              required
              :class="{
                'custom-select is-valid': !v$.variant_origin.$error,
                'custom-select is-invalid': v$.variant_origin.$error,
              }"
            >
              <option>Chose...</option>
              <option
                v-for="variantOriginOption in VARIANT_ORIGIN_OPTIONS"
                :key="variantOriginOption"
                :value="variantOriginOption"
              >
                {{ variantOriginOption }}
              </option>
            </select>
            <div
              v-for="error of v$.variant_origin.$errors"
              :key="error.$uid"
              class="invalid-feedback"
            >
              {{ error.$message }}
            </div>
          </div>
        </div>
        <div class="col-4">
          <div id="input-group-alle-count" class="form-group">
            <label for="input-source">Variant Allele Count</label>
            <input
              id="input-variant-allele-count"
              v-model="v$.variant_allele_count.$model"
              required
              :class="{
                'form-control is-valid': !v$.variant_allele_count.$error,
                'form-control is-invalid': v$.variant_allele_count.$error,
              }"
            />
            <div
              v-for="error of v$.variant_allele_count.$errors"
              :key="error.$uid"
              class="invalid-feedback"
            >
              {{ error.$message }}
            </div>
          </div>
        </div>
        <div class="col-4 pr-0">
          <div id="input-group-variant-zygosity" class="form-group">
            <label for="input-source">Variant Zygosity</label>
            <select
              id="input-variant-zygosity"
              v-model="v$.variant_zygosity.$model"
              required
              :class="{
                'custom-select is-valid': !v$.variant_zygosity.$error,
                'custom-select is-invalid': v$.variant_zygosity.$error,
              }"
            >
              <option>Chose...</option>
              <option
                v-for="variantZygosityOption in VARIANT_ZYGOSITY_OPTIONS"
                :key="variantZygosityOption"
                :value="variantZygosityOption"
              >
                {{ variantZygosityOption }}
              </option>
            </select>
            <div
              v-for="error of v$.variant_zygosity.$errors"
              :key="error.$uid"
              class="invalid-feedback"
            >
              {{ error.$message }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.is-invalid .multiselect__tags {
  border-color: #dc3545;
}
.is-valid .multiselect__tags {
  border-color: #28a745;
}
</style>
