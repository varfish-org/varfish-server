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
          v-model.trim.lazy="title"
          :class="{
            'form-control is-valid': !$v.title.$error,
            'form-control is-invalid': $v.title.$error,
          }"
          placeholder="Enter submission title"
          required
        />
        <div v-if="!$v.title.required" class="invalid-feedback">
          Field is required.
        </div>
        <div v-if="!$v.title.minLength" class="invalid-feedback">
          Must be set with at least 3 character.
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
          v-model="submitter"
          :class="{
            'custom-select is-valid': !$v.submitter.$error,
            'custom-select is-invalid': $v.submitter.$error,
          }"
          required
        >
          <option>Chose...</option>
          <option
            v-for="submitter in submitters"
            :key="submitter.sodar_uuid"
            :value="submitter.sodar_uuid"
          >
            {{ submitter.name }}
          </option>
        </select>
        <div v-if="!$v.submitter.required" class="invalid-feedback">
          Must be provided.
        </div>
        <div v-if="!$v.submitter.validChoice" class="invalid-feedback">
          Must be a valid choice.
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
          v-model="state"
          :class="{
            'custom-select is-valid': !$v.state.$error,
            'custom-select is-invalid': $v.state.$error,
          }"
          required
        >
          <option>Chose...</option>
          <option v-for="state in stateChoices" :key="state" :value="state">
            {{ state }}
          </option>
        </select>
        <div v-if="!$v.submitter.required" class="invalid-feedback">
          Must be provided.
        </div>
        <div v-if="!$v.submitter.validChoice" class="invalid-feedback">
          Must be a valid choice.
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
          v-model="organisations"
          placeholder="Select submitting organisations"
          required
          :options="orgUuids"
          :custom-label="getOrgLabel"
          :multiple="true"
          :close-on-select="false"
          :class="{
            'is-valid': !$v.organisations.$error,
            'is-invalid': $v.organisations.$error,
          }"
          aria-describedby="input-group-organisations-feedback"
        ></multiselect>
        <div v-if="!$v.organisations.required" class="invalid-feedback">
          You must select at least one organisation.
        </div>
        <div v-if="!$v.organisations.validChoice" class="invalid-feedback">
          Organisations must be valid.
        </div>
        <small class="form-text text-muted">
          Select one or more submitting organisations. The first one will become
          the primary submitter.
        </small>
      </div>
    </form>
  </div>
</template>

<script>
import Multiselect from 'vue-multiselect'
import { validationMixin } from 'vuelidate'
import { minLength, required } from 'vuelidate/lib/validators'
import { mapActions, mapState } from 'vuex'

const STATE_CHOICES = Object.freeze([
  'draft',
  'discontinued',
  'pending',
  'submitted',
  'released',
  'rejected',
])

function generateVuexVuelidateWrappers(keys) {
  return Object.fromEntries(
    keys.map((key) => [
      key,
      {
        get() {
          return this.currentSubmissionSet[key]
        },
        set(value) {
          this.updateCurrentSubmissionSet({ key, value })
          this.$v[key].$touch()
        },
      },
    ])
  )
}

export default {
  components: { Multiselect },
  mixins: [validationMixin],
  computed: {
    ...mapState({
      orgs: (state) => state.clinvarExport.organisations,
      submitters: (state) => state.clinvarExport.submitters,
      submittingOrgs: (state) => state.clinvarExport.submittingOrgs,
      currentSubmissionSet: (state) => state.clinvarExport.currentSubmissionSet,
    }),

    ...generateVuexVuelidateWrappers(['title', 'submitter', 'state']),

    organisations: {
      get() {
        return this.currentSubmissionSet.submitting_orgs.map(
          (soUuid) =>
            this.orgs[this.submittingOrgs[soUuid].organisation].sodar_uuid
        )
      },
      set(value) {
        this.updateCurrentSubmissionSetOrganisations(value)
      },
    },

    stateChoices() {
      return STATE_CHOICES
    },
    submitterChoices: function () {
      return Array.from(Object.values(this.submitters), (o) => ({
        value: o.sodar_uuid,
        text: o.name,
      }))
    },
    submitterUuids: function () {
      return Array.from(Object.values(this.submitters), (o) => o.sodar_uuid)
    },
    orgUuids: function () {
      return Array.from(Object.values(this.orgs), (o) => o.sodar_uuid)
    },
  },
  validations: {
    title: {
      required,
      minLength: minLength(3),
    },
    state: {
      required,
      validChoice: (x) => STATE_CHOICES.includes(x),
    },
    submitter: {
      required,
      validChoice: function (x) {
        return this.submitterUuids.includes(x)
      },
    },
    organisations: {
      required: (x) => {
        return x && x.length
      },
      validChoice: function (orgUuids) {
        for (const orgUuid of orgUuids) {
          if (!this.orgUuids.includes(orgUuid)) {
            return false
          }
        }
        return true
      },
    },
  },
  mounted() {
    this.$v.$touch()
  },
  methods: {
    ...mapActions('clinvarExport', [
      'updateCurrentSubmissionSetOrganisations',
      'updateCurrentSubmissionSet',
    ]),

    getOrgLabel(orgUuid) {
      return this.orgs[orgUuid].name
    },
    validateState(name) {
      const { $dirty, $error } = this.$v[name]
      return $dirty ? !$error : null
    },
    isValid() {
      return !this.$v.$invalid
    },
  },
}
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style>
.is-invalid .multiselect__tags {
  border-color: #dc3545;
}
.is-valid .multiselect__tags {
  border-color: #28a745;
}
</style>
