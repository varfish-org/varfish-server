<template>
  <b-card-body>
    <b-alert variant="info" class="small pl-3" show>
      <i class="iconify mr-1" data-icon="fa-solid:info-circle"></i>
      A Clinvar submission set consists of multiple variants (aka submissions).
      Edit the base properties here and continue by clicking "Variants" on the bottom right.
      Click "Save" to save the submission and go back to the list and use "Cancel" to discard changes and go back to the list without saving them.
    </b-alert>
    <b-form>
      <b-form-group id="input-group-title" label-for="input-title" label="Title">
        <b-form-input
          id="input-title"
          placeholder="Enter submission title"
          required
          v-model.trim.lazy="title"
          :state="validateState('title')"
          aria-describedby="input-group-title-feedback"
        ></b-form-input>
        <b-form-invalid-feedback
          id="input-group-title-feedback"
        >Must be set with at least 3 characters.</b-form-invalid-feedback>
      </b-form-group>

      <b-form-group
        id="input-group-submitter"
        label-for="input-submitter"
        label="Submitter"
        description="person who will do the ClinVar XML submission (must register through ClinVar web interface)"
      >
        <b-form-select
          id="input-submitter"
          v-model="submitter"
          :options="submitterChoices"
          :state="validateState('submitter')"
          aria-describedby="input-group-submitter-feedback"
        ></b-form-select>
        <b-form-invalid-feedback
          id="input-group-submitter-feedback"
        >Must be a valid choice.</b-form-invalid-feedback>
      </b-form-group>

      <b-form-group
        id="input-group-state"
        label-for="input-state"
        label="State"
        description="pending: not submitted yet, submitted: submitted to Clinvar, released: released by Clinvar, rejected: rejected by Clinvar, pending resubmission"
      >
        <b-form-select
          id="input-state"
          v-model="state"
          :options="stateChoices"
          :state="validateState('state')"
          aria-describedby="input-group-state-feedback"
        ></b-form-select>
        <b-form-invalid-feedback
          id="input-group-state-feedback"
        >Must be a valid choice.</b-form-invalid-feedback>
      </b-form-group>

      <b-form-group
        id="input-group-organisations"
        label-for="input-organisations"
        label="Submitting Organisations"
        description="Select one or more submitting organisations. The first one will become the primary submitter."
      >
        <multiselect
          id="input-organisations"
          placeholder="Select submitting organisations"
          required
          :options="orgUuids"
          :customLabel="getOrgLabel"
          :multiple="true"
          :close-on-select="false"
          v-model="organisations"
          aria-describedby="input-group-organisations-feedback"
        ></multiselect>
        <b-form-invalid-feedback
          id="input-group-organisations-feedback"
        >You must select at least one organisation.</b-form-invalid-feedback>
      </b-form-group>
    </b-form>
  </b-card-body>
</template>

<script>
import { required, minLength } from 'vuelidate/lib/validators'
import { validationMixin } from 'vuelidate'
import Multiselect from 'vue-multiselect'
import { mapActions, mapState } from 'vuex'

const STATE_CHOICES = Object.freeze(['draft', 'discontinued', 'pending', 'submitted', 'released', 'rejected'])

function generateVuexVuelidateWrappers (keys) {
  return Object.fromEntries(
    keys.map(key => [key, {
      get () {
        return this.currentSubmissionSet[key]
      },
      set (value) {
        this.updateCurrentSubmissionSet({ key, value })
        this.$v[key].$touch()
      }
    }])
  )
}

export default {
  mixins: [validationMixin],
  components: { Multiselect },
  computed: {
    ...mapState({
      orgs: state => state.clinvarExport.organisations,
      submitters: state => state.clinvarExport.submitters,
      submittingOrgs: state => state.clinvarExport.submittingOrgs,
      currentSubmissionSet: state => state.clinvarExport.currentSubmissionSet
    }),

    ...generateVuexVuelidateWrappers([
      'title',
      'submitter',
      'state'
    ]),

    organisations: {
      get () {
        return this.currentSubmissionSet.submitting_orgs
          .map(soUuid => this.orgs[this.submittingOrgs[soUuid].organisation].sodar_uuid)
      },
      set (value) {
        this.updateCurrentSubmissionSetOrganisations(value)
      }
    },

    stateChoices () {
      return STATE_CHOICES
    },
    submitterChoices: function () {
      return Array.from(
        Object.values(this.submitters),
        o => ({ value: o.sodar_uuid, text: o.name })
      )
    },
    orgUuids: function () {
      return Array.from(Object.values(this.orgs), o => o.sodar_uuid)
    }
  },
  validations: {
    title: {
      required,
      minLength: minLength(3)
    },
    state: {
      required,
      isValidStateChoice: (x) => STATE_CHOICES.includes(x)
    },
    submitter: {
      required
    },
    organisations: {
      required
    }
  },
  mounted () {
    this.$v.$touch()
  },
  methods: {
    ...mapActions('clinvarExport', [
      'updateCurrentSubmissionSetOrganisations',
      'updateCurrentSubmissionSet'
    ]),

    getOrgLabel (orgUuid) {
      return this.orgs[orgUuid].name
    },
    validateState (name) {
      const { $dirty, $error } = this.$v[name]
      return $dirty ? !$error : null
    },
    isValid () {
      return !this.$v.$invalid
    }
  }
}
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style scoped>
</style>
