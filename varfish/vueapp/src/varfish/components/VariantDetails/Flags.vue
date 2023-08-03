<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import isEqual from 'lodash.isequal'

import { copy } from '@varfish/helpers'
import Overlay from '@varfish/components/Overlay.vue'

/** The stores and small/large variant are handed in via props. */
const props = defineProps({
  detailsStore: Object,
  flagsStore: Object,
  variant: Object,
})

/** Whether to show the overlay. */
const overlayShow = computed(
  () => (props.flagsStore?.serverInteractions ?? 0) > 0,
)

const flagsToSubmit = ref(copy({ ...props.flagsStore.initialFlagsTemplate }))

const unsetFlags = () => {
  flagsToSubmit.value = copy(props.flagsStore.emptyFlagsTemplate)
}

const flagsSubmitted = computed(() => {
  if (!props.flagsStore.flags) {
    return false
  }
  return (
    flagsToSubmit.value.flag_bookmarked ===
      props.flagsStore.flags.flag_bookmarked &&
    flagsToSubmit.value.flag_for_validation ===
      props.flagsStore.flags.flag_for_validation &&
    flagsToSubmit.value.flag_candidate ===
      props.flagsStore.flags.flag_candidate &&
    flagsToSubmit.value.flag_final_causative ===
      props.flagsStore.flags.flag_final_causative &&
    flagsToSubmit.value.flag_no_disease_association ===
      props.flagsStore.flags.flag_no_disease_association &&
    flagsToSubmit.value.flag_segregates ===
      props.flagsStore.flags.flag_segregates &&
    flagsToSubmit.value.flag_doesnt_segregate ===
      props.flagsStore.flags.flag_doesnt_segregate &&
    flagsToSubmit.value.flag_visual === props.flagsStore.flags.flag_visual &&
    flagsToSubmit.value.flag_molecular ===
      props.flagsStore.flags.flag_molecular &&
    flagsToSubmit.value.flag_validation ===
      props.flagsStore.flags.flag_validation &&
    flagsToSubmit.value.flag_phenotype_match ===
      props.flagsStore.flags.flag_phenotype_match &&
    flagsToSubmit.value.flag_summary === props.flagsStore.flags.flag_summary
  )
})

const resetFlags = () => {
  if (props.flagsStore.flags) {
    flagsToSubmit.value.flag_bookmarked = props.flagsStore.flags.flag_bookmarked
    flagsToSubmit.value.flag_for_validation =
      props.flagsStore.flags.flag_for_validation
    flagsToSubmit.value.flag_candidate = props.flagsStore.flags.flag_candidate
    flagsToSubmit.value.flag_final_causative =
      props.flagsStore.flags.flag_final_causative
    flagsToSubmit.value.flag_no_disease_association =
      props.flagsStore.flags.flag_no_disease_association
    flagsToSubmit.value.flag_segregates = props.flagsStore.flags.flag_segregates
    flagsToSubmit.value.flag_doesnt_segregate =
      props.flagsStore.flags.flag_doesnt_segregate
    flagsToSubmit.value.flag_visual = props.flagsStore.flags.flag_visual
    flagsToSubmit.value.flag_molecular = props.flagsStore.flags.flag_molecular
    flagsToSubmit.value.flag_validation = props.flagsStore.flags.flag_validation
    flagsToSubmit.value.flag_phenotype_match =
      props.flagsStore.flags.flag_phenotype_match
    flagsToSubmit.value.flag_summary = props.flagsStore.flags.flag_summary
  } else {
    flagsToSubmit.value = { ...props.flagsStore.initialFlagsTemplate }
  }
}

const onSubmitFlags = async () => {
  const flagsToSubmitEmpty = isEqual(
    flagsToSubmit.value,
    props.flagsStore.emptyFlagsTemplate,
  )
  if (props.flagsStore.flags && flagsToSubmitEmpty) {
    // IS not empty but SHOULD be empty, so delete the flags
    await props.flagsStore.deleteFlags()
  } else if (!props.flagsStore.flags && flagsToSubmitEmpty) {
    // IS empty and SHOULD be empty, so no update needed
    flagsToSubmit.value = copy(props.flagsStore.initialFlagsTemplate)
  } else if (props.flagsStore.flags && !flagsToSubmitEmpty) {
    // IS not empty and SHOULD not be empty, so update the flags
    await props.flagsStore.updateFlags(flagsToSubmit.value)
  } else if (!props.flagsStore.flags && !flagsToSubmitEmpty) {
    // IS empty but SHOULD not be empty, so create the flags
    await props.flagsStore.createFlags(props.variant, flagsToSubmit.value)
  }
}

watch(
  () => [props.variant, props.flagsStore.storeState],
  () => {
    if (props.variant && props.flagsStore.storeState === 'active') {
      props.flagsStore.retrieveFlags(props.variant).then(() => {
        resetFlags()
      })
    }
  },
)

onMounted(() => {
  if (props.variant) {
    props.flagsStore.retrieveFlags(props.variant).then(() => {
      resetFlags()
    })
  }
})
</script>

<template>
  <div
    class="varfish-overlay-wrap position-relative flex-grow-1 d-flex flex-column"
  >
    <div class="p-2">
      <div class="row">
        <div class="col-4">
          <div class="form-check form-check-inline">
            <input
              type="checkbox"
              id="flagBookmarked"
              name="flag_bookmarked"
              class="form-check-input"
              v-model="flagsToSubmit.flag_bookmarked"
            />
            <label
              for="flagBookmarked"
              title="bookmarked"
              class="form-check-label"
            >
              <i-fa-solid-star />
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input
              type="checkbox"
              id="flagForValidation"
              name="flag_for_validation"
              class="form-check-input"
              v-model="flagsToSubmit.flag_for_validation"
            />
            <label
              for="flagForValidation"
              title="selected for validation"
              class="form-check-label"
            >
              <i-fa-solid-flask />
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input
              type="checkbox"
              id="flagCandidate"
              name="flag_candidate"
              class="form-check-input"
              v-model="flagsToSubmit.flag_candidate"
            />
            <label
              for="flagCandidate"
              title="candidate variant"
              class="form-check-label"
            >
              <i-fa-solid-heart />
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input
              type="checkbox"
              id="flagFinalCausative"
              name="flag_final_causative"
              class="form-check-input"
              v-model="flagsToSubmit.flag_final_causative"
            />
            <label
              for="flagFinalCausative"
              title="final causative/reported"
              class="form-check-label"
            >
              <i-fa-solid-flag-checkered />
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input
              type="checkbox"
              id="flagNoDiseaseAssociation"
              name="flag_no_disease_association"
              class="form-check-input"
              v-model="flagsToSubmit.flag_no_disease_association"
            />
            <label
              for="flagNoDiseaseAssociation"
              title="gene affected by this variant has no known disease association"
              class="form-check-label"
            >
              <i-cil-link-broken />
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input
              type="checkbox"
              id="flagDoesSegregate"
              name="flag_segregates"
              class="form-check-input"
              v-model="flagsToSubmit.flag_segregates"
            />
            <label
              for="flagDoesSegregate"
              title="variant does segregate"
              class="form-check-label"
            >
              <i-fa-solid-thumbs-up />
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input
              type="checkbox"
              id="flagDoesntSegregate"
              name="flag_doesnt_segregate"
              class="form-check-input"
              v-model="flagsToSubmit.flag_doesnt_segregate"
            />
            <label
              for="flagDoesntSegregate"
              title="variant doesn't segregate"
              class="form-check-label"
            >
              <i-fa-solid-thumbs-down />
            </label>
          </div>
        </div>
        <div class="col-1">
          <strong> Visual </strong>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorVisual-positive"
              value="positive"
              v-model="flagsToSubmit.flag_visual"
            />
            <label for="flagSelectorVisual-positive" class="form-check-label">
              <i-fa-solid-exclamation-circle class="text-danger" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorVisual-uncertain"
              value="uncertain"
              v-model="flagsToSubmit.flag_visual"
            />
            <label for="flagSelectorVisual-uncertain" class="form-check-label">
              <i-fa-solid-question class="text-warning" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorVisual-negative"
              value="negative"
              v-model="flagsToSubmit.flag_visual"
            />
            <label for="flagSelectorVisual-negative" class="form-check-label">
              <i-fa-solid-minus-circle class="text-success" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorVisual-empty"
              value="empty"
              v-model="flagsToSubmit.flag_visual"
            />
            <label for="flagSelectorVisual-empty" class="form-check-label">
              <i-fa-solid-times class="text-secondary" />
            </label>
          </div>
        </div>
        <div class="col-1">
          <strong> Molecular </strong>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorMolecular-positive"
              value="positive"
              v-model="flagsToSubmit.flag_molecular"
            />
            <label
              for="flagSelectorMolecular-positive"
              class="form-check-label"
            >
              <i-fa-solid-exclamation-circle class="text-danger" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorMolecular-uncertain"
              value="uncertain"
              v-model="flagsToSubmit.flag_molecular"
            />
            <label
              for="flagSelectorMolecular-uncertain"
              class="form-check-label"
            >
              <i-fa-solid-question class="text-warning" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorMolecular-negative"
              value="negative"
              v-model="flagsToSubmit.flag_molecular"
            />
            <label
              for="flagSelectorMolecular-negative"
              class="form-check-label"
            >
              <i-fa-solid-minus-circle class="text-success" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorMolecular-empty"
              value="empty"
              v-model="flagsToSubmit.flag_molecular"
            />
            <label for="flagSelectorMolecular-empty" class="form-check-label">
              <i-fa-solid-times class="text-secondary" />
            </label>
          </div>
        </div>
        <div class="col-1">
          <strong> Validation </strong>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorValidation-positive"
              value="positive"
              v-model="flagsToSubmit.flag_validation"
            />
            <label
              for="flagSelectorValidation-positive"
              class="form-check-label"
            >
              <i-fa-solid-exclamation-circle class="text-danger" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorValidation-uncertain"
              value="uncertain"
              v-model="flagsToSubmit.flag_validation"
            />
            <label
              for="flagSelectorValidation-uncertain"
              class="form-check-label"
            >
              <i-fa-solid-question class="text-warning" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorValidation-negative"
              value="negative"
              v-model="flagsToSubmit.flag_validation"
            />
            <label
              for="flagSelectorValidation-negative"
              class="form-check-label"
            >
              <i-fa-solid-minus-circle class="text-success" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorValidation-empty"
              value="empty"
              v-model="flagsToSubmit.flag_validation"
            />
            <label for="flagSelectorValidation-empty" class="form-check-label">
              <i-fa-solid-times class="text-secondary" />
            </label>
          </div>
        </div>
        <div class="col-1">
          <strong> Phenotype </strong>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorPhenotype-positive"
              value="positive"
              v-model="flagsToSubmit.flag_phenotype_match"
            />
            <label
              for="flagSelectorPhenotype-positive"
              class="form-check-label"
            >
              <i-fa-solid-exclamation-circle class="text-danger" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorPhenotype-uncertain"
              value="uncertain"
              v-model="flagsToSubmit.flag_phenotype_match"
            />
            <label
              for="flagSelectorPhenotype-uncertain"
              class="form-check-label"
            >
              <i-fa-solid-question class="text-warning" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorPhenotype-negative"
              value="negative"
              v-model="flagsToSubmit.flag_phenotype_match"
            />
            <label
              for="flagSelectorPhenotype-negative"
              class="form-check-label"
            >
              <i-fa-solid-minus-circle class="text-success" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorPhenotype-empty"
              value="empty"
              v-model="flagsToSubmit.flag_phenotype_match"
            />
            <label for="flagSelectorPhenotype-empty" class="form-check-label">
              <i-fa-solid-times class="text-secondary" />
            </label>
          </div>
        </div>
        <div class="col-1">
          <strong>
            <u>Summary</u>
          </strong>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorSummary-positive"
              value="positive"
              v-model="flagsToSubmit.flag_summary"
            />
            <label for="flagSelectorSummary-positive" class="form-check-label">
              <i-fa-solid-exclamation-circle class="text-danger" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorSummary-uncertain"
              value="uncertain"
              v-model="flagsToSubmit.flag_summary"
            />
            <label for="flagSelectorSummary-uncertain" class="form-check-label">
              <i-fa-solid-question class="text-warning" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorSummary-negative"
              value="negative"
              v-model="flagsToSubmit.flag_summary"
            />
            <label for="flagSelectorSummary-negative" class="form-check-label">
              <i-fa-solid-minus-circle class="text-success" />
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="flagSelectorSummary-empty"
              value="empty"
              v-model="flagsToSubmit.flag_summary"
            />
            <label for="flagSelectorSummary-empty" class="form-check-label">
              <i-fa-solid-times class="text-secondary" />
            </label>
          </div>
        </div>
        <div class="col">
          <div class="btn-group pull-right">
            <button class="btn btn-sm btn-secondary" @click="unsetFlags()">
              Clear
            </button>
            <button class="btn btn-sm btn-secondary" @click="resetFlags()">
              Reset
            </button>
            <button
              class="btn btn-sm"
              :class="flagsSubmitted ? 'btn-success' : 'btn-primary'"
              @click="onSubmitFlags()"
            >
              <i-fa-solid-flag v-if="flagsSubmitted" />
              <i-fa-regular-flag v-else />
              Submit
            </button>
          </div>
        </div>
      </div>
      <div class="row pt-2">
        <div
          class="col-12 alert alert-secondary small text-muted p-1 pl-2 pr-2"
        >
          <i-fa-solid-info-circle />
          Value in <strong><u>Summary</u></strong> will determine the row
          coloring in the results table. If <code>empty</code>, any other flag
          set except <i-fa-solid-star /> will color the row in gray.
          <span class="badge badge-primary">Submit</span> indicates that there
          are changes not yet submitted, while
          <span class="badge badge-success">Submit</span> indicates that changes
          have been submitted or not made at all. Press
          <span class="badge badge-secondary">Reset</span> to reset the flags to
          the last submitted state. Press
          <span class="badge badge-secondary">Clear</span> and
          <span class="badge badge-primary">Submit</span> to delete all flags.
        </div>
      </div>
    </div>
    <Overlay v-if="overlayShow" />
  </div>
</template>
