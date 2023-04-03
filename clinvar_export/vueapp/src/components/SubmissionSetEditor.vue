<script setup>
import { ref, computed, onMounted } from 'vue'
import Multiselect from '@vueform/multiselect'
import { useVuelidate } from '@vuelidate/core'
import { minLength, required } from '@vuelidate/validators'
import FetchClinVarReport from './FetchClinVarReport.vue'

import {
  SUBMISSION_SET_STATE_CHOICES,
  useClinvarExportStore,
} from '@clinvarexport/stores/clinvar-export'

const components = { Multiselect }

// Define Pinia store and shortcut for currentSubmissionSet
const store = useClinvarExportStore()
const currentSubmissionSet = ref(store.currentSubmissionSet)

// These values are used in the form and validation.
const submitterUuids = computed(() =>
  Array.from(Object.values(store.submitters), (o) => o.sodar_uuid)
)
const orgOptions = computed(() => {
  let result = Object.fromEntries(
    Object.values(store.organisations).map((o) => [o.sodar_uuid, o.name])
  )
  return result
})

// Helper function to build wrappers that catch the case of store.currentSubmissionSet not being set.
const _vuelidateWrappers = (keys) =>
  Object.fromEntries(
    keys.map((key) => [
      key,
      computed({
        get() {
          return !currentSubmissionSet.value
            ? null
            : currentSubmissionSet.value[key]
        },
        set(newValue) {
          if (currentSubmissionSet.value) {
            currentSubmissionSet.value[key] = newValue
          }
        },
      }),
    ])
  )

// Define object with the data to edit in the form.  We construct custom wrappers so we can easily pass this into vuelidate.
const formState = {
  ..._vuelidateWrappers(['title', 'state', 'submitter']),
  organisations: computed({
    get() {
      if (
        !currentSubmissionSet.value ||
        !currentSubmissionSet.value.submitting_orgs
      ) {
        return null
      }
      const result = currentSubmissionSet.value.submitting_orgs.map(
        (soUuid) =>
          store.organisations[store.submittingOrgs[soUuid].organisation]
            .sodar_uuid
      )
      return result
    },
    set(value) {
      if (!currentSubmissionSet.value) {
        return
      }
      store.updateCurrentSubmissionSetOrganisations(value)
    },
  }),
}
// Define validation rules.
const rules = computed(() => {
  if (currentSubmissionSet.value) {
    return {
      title: {
        required,
        minLength: minLength(3),
        $autoDirty: true,
      },
      state: {
        required,
        validChoice: (x) => SUBMISSION_SET_STATE_CHOICES.includes(x),
      },
      submitter: {
        required,
        validChoice: function (x) {
          return submitterUuids.value.includes(x)
        },
      },
      organisations: {
        required: (x) => {
          return x && x.length
        },
        validChoice: function (orgUuids) {
          for (const orgUuid of orgUuids) {
            if (!orgUuids.includes(orgUuid)) {
              return false
            }
          }
          return true
        },
      },
    }
  } else {
    return {}
  }
})

// Define vuelidate object
const v$ = useVuelidate(rules, formState)

onMounted(() => {
  v$.value.$touch()
})

// Helper method to return label for an organisation UUID
const getOrgLabel = (orgUuid) => {
  if (store.organisations && store.organisations[orgUuid]) {
    return store.organisations[orgUuid].name
  } else {
    return ''
  }
}

/**
 * @returns {boolean} <code>true</code> if there are no validation errors and <code>false</code> otherwise
 */
const isValid = () => !v$.$errors

// Define the exposed functions
defineExpose({
  isValid,
})
</script>

<template>
  <div class="card-body">
    <div class="alert alert-info small pl-3">
      <i class="iconify mr-1" data-icon="fa-solid:info-circle"></i>
      A Clinvar submission set consists of multiple variants (aka submissions).
      Edit the base properties here and continue by clicking "Variants" on the
      bottom right. Click "Save" to save the submission and go back to the list
      and use "Cancel" to discard changes and go back to the list without saving
      them.
    </div>
    <form>
      <div id="input-group-title" class="form-group">
        <label for="input-title">Title</label>
        <input
          id="input-title"
          v-model.trim.lazy="v$.title.$model"
          :class="{
            'form-control is-valid': !v$.title.$error,
            'form-control is-invalid': v$.title.$error,
          }"
          placeholder="Enter submission title"
          required
        />
        <div
          v-for="error of v$.title.$errors"
          :key="error.$uid"
          class="invalid-feedback"
        >
          {{ error.$message }}
        </div>
        <small class="form-text text-muted">
          The title of the submission is only used for display in VarFish and
          not submitted to ClinVar.
        </small>
      </div>

      <div id="input-group-submitter" class="form-group">
        <label for="input-submitter">Submitter</label>
        <select
          id="input-submitter"
          v-model="v$.submitter.$model"
          :class="{
            'custom-select is-valid': !v$.submitter.$error,
            'custom-select is-invalid': v$.submitter.$error,
          }"
          required
        >
          <option>Chose...</option>
          <option
            v-for="submitter in store.submitters"
            :key="submitter.sodar_uuid"
            :value="submitter.sodar_uuid"
          >
            {{ submitter.name }}
          </option>
        </select>
        <div
          v-for="error of v$.submitter.$errors"
          :key="error.$uid"
          class="invalid-feedback"
        >
          {{ error.$message }}
        </div>
        <small class="form-text text-muted">
          The person who will do the ClinVar XML submission (must register
          through ClinVar web interface).
        </small>
      </div>

      <div id="input-group-state" class="form-group">
        <label for="input-state">Submission Set State</label>
        <select
          id="input-state"
          v-model="v$.state.$model"
          :class="{
            'custom-select is-valid': !v$.state.$error,
            'custom-select is-invalid': v$.state.$error,
          }"
          required
        >
          <option>Chose...</option>
          <option
            v-for="state in SUBMISSION_SET_STATE_CHOICES"
            :key="state"
            :value="state"
          >
            {{ state }}
          </option>
        </select>
        <div
          v-for="error of v$.state.$errors"
          :key="error.$uid"
          class="invalid-feedback"
        >
          {{ error.$message }}
        </div>
        <small class="form-text text-muted">
          The person who will do the ClinVar XML submission (must register
          through ClinVar web interface).
        </small>
      </div>

      <div id="input-group-organisations" class="form-group">
        <label for="input-organisations">Submitting Organisation(s)</label>
        <multiselect
          id="input-organisations"
          v-model="v$.organisations.$model"
          placeholder="Select submitting organisations"
          mode="tags"
          :options="orgOptions"
          :custom-label="getOrgLabel"
          :searchable="true"
          :close-on-select="false"
          :class="{
            'is-valid': !v$.organisations.$error,
            'is-invalid': v$.organisations.$error,
          }"
          aria-describedby="input-group-organisations-feedback"
        ></multiselect>
        <div
          v-for="error of v$.organisations.$errors"
          :key="error.$uid"
          class="invalid-feedback"
        >
          {{ error.$message }}
        </div>
        <small class="form-text text-muted">
          Select one or more submitting organisations. The first one will become
          the primary submitter.
        </small>
      </div>

      <h4>Fetch ClinVar Report</h4>

      <FetchClinVarReport
        :app-context="store.appContext"
        :submission-set="currentSubmissionSet"
      />
    </form>
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

<style src="@vueform/multiselect/themes/default.css"></style>
