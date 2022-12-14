<script setup>
import { ref, watch } from 'vue'
import isEqual from 'lodash.isequal'

import { useVariantDetailsStore } from '@variants/stores/variantDetails.js'
import {
  useVariantFlagsStore,
  initialFlagsTemplate,
  emptyFlagsTemplate,
} from '@variants/stores/variantFlags.js'
import { copy } from '@varfish/helpers.js'

import VariantDetailsFlagsIndicator from './VariantDetailsFlagsIndicator.vue'

const detailsStore = useVariantDetailsStore()
const flagsStore = useVariantFlagsStore()

const setFlagsMode = ref(false)
const flagsToSubmit = ref(copy({ ...initialFlagsTemplate }))

const unsetFlags = () => {
  flagsToSubmit.value = copy(emptyFlagsTemplate)
}

const resetFlags = () => {
  if (flagsStore.flags) {
    flagsToSubmit.value.flag_bookmarked = flagsStore.flags.flag_bookmarked
    flagsToSubmit.value.flag_for_validation =
      flagsStore.flags.flag_for_validation
    flagsToSubmit.value.flag_candidate = flagsStore.flags.flag_candidate
    flagsToSubmit.value.flag_final_causative =
      flagsStore.flags.flag_final_causative
    flagsToSubmit.value.flag_no_disease_association =
      flagsStore.flags.flag_no_disease_association
    flagsToSubmit.value.flag_segregates = flagsStore.flags.flag_segregates
    flagsToSubmit.value.flag_doesnt_segregate =
      flagsStore.flags.flag_doesnt_segregate
    flagsToSubmit.value.flag_visual = flagsStore.flags.flag_visual
    flagsToSubmit.value.flag_molecular = flagsStore.flags.flag_molecular
    flagsToSubmit.value.flag_validation = flagsStore.flags.flag_validation
    flagsToSubmit.value.flag_phenotype_match =
      flagsStore.flags.flag_phenotype_match
    flagsToSubmit.value.flag_summary = flagsStore.flags.flag_summary
  } else {
    flagsToSubmit.value = { ...initialFlagsTemplate }
  }
}

flagsStore.initialize(
  { csrf_token: detailsStore.csrfToken },
  detailsStore.smallVariant.case_uuid
)
flagsStore.retrieveFlags(detailsStore.smallVariant).then(() => {
  resetFlags()
})

const onSubmitFlags = async () => {
  const flagsToSubmitEmpty = isEqual(flagsToSubmit.value, emptyFlagsTemplate)
  if (flagsStore.flags && flagsToSubmitEmpty) {
    // IS not empty but SHOULD be empty, so delete the flags
    await flagsStore.deleteFlags()
  } else if (!flagsStore.flags && flagsToSubmitEmpty) {
    // IS empty and SHOULD be empty, so no update needed
    flagsToSubmit.value = copy(initialFlagsTemplate)
  } else if (flagsStore.flags && !flagsToSubmitEmpty) {
    // IS not empty and SHOULD not be empty, so update the flags
    await flagsStore.updateFlags(flagsToSubmit.value)
  } else if (!flagsStore.flags && !flagsToSubmitEmpty) {
    // IS empty but SHOULD not be empty, so create the flags
    await flagsStore.createFlags(detailsStore.smallVariant, flagsToSubmit.value)
  }
  setFlagsMode.value = false
}

const cancelFlags = () => {
  resetFlags()
  setFlagsMode.value = false
}

const displayMutedIfFalse = (condition) => {
  if (!condition) {
    return 'text-muted'
  } else {
    return 'text-dark'
  }
}

const displayOpacityIfFalse = (condition) => {
  if (!condition) {
    return 'opacity: 20%'
  } else {
    return ''
  }
}
</script>

<template>
  <div
    v-if="flagsStore.flags && !setFlagsMode"
    class="row font-weight-bold p-2"
  >
    <div class="col">
      <div class="row">
        <div class="col-1 pl-0">
          <i-fa-solid-star
            :class="displayMutedIfFalse(flagsStore.flags.flag_bookmarked)"
            :style="displayOpacityIfFalse(flagsStore.flags.flag_bookmarked)"
          />
        </div>
        <div class="col-1 pl-1">
          <i-fa-solid-flask
            :class="displayMutedIfFalse(flagsStore.flags.flag_for_validation)"
            :style="displayOpacityIfFalse(flagsStore.flags.flag_for_validation)"
          />
        </div>
        <div class="col-1 pl-1">
          <i-fa-solid-heart
            class="ml-1"
            :class="displayMutedIfFalse(flagsStore.flags.flag_candidate)"
            :style="displayOpacityIfFalse(flagsStore.flags.flag_candidate)"
          />
        </div>
        <div class="col-1 pl-1">
          <i-fa-solid-flag-checkered
            class="ml-1"
            :class="displayMutedIfFalse(flagsStore.flags.flag_final_causative)"
            :style="
              displayOpacityIfFalse(flagsStore.flags.flag_final_causative)
            "
            data-icon="fa-solid:flag-checkered"
          />
        </div>
        <div class="col-1 pl-1">
          <i-cil-link-broken
            class="ml-1"
            :class="
              displayMutedIfFalse(flagsStore.flags.flag_no_disease_association)
            "
            :style="
              displayOpacityIfFalse(
                flagsStore.flags.flag_no_disease_association
              )
            "
          />
        </div>
        <div class="col-1 pl-1">
          <i-fa-solid-thumbs-up
            class="ml-1"
            :class="displayMutedIfFalse(flagsStore.flags.flag_segregates)"
            :style="displayOpacityIfFalse(flagsStore.flags.flag_segregates)"
          />
        </div>
        <div class="col-1 pl-1">
          <i-fa-solid-thumbs-down
            class="ml-1"
            :class="displayMutedIfFalse(flagsStore.flags.flag_doesnt_segregate)"
            :style="
              displayOpacityIfFalse(flagsStore.flags.flag_doesnt_segregate)
            "
          />
        </div>
      </div>
    </div>
    <div class="col-8">
      <div class="row text-center">
        <div class="col">
          Visual
          <VariantDetailsFlagsIndicator
            :flag-state="flagsStore.flags.flag_visual"
          />
        </div>
        <div class="col">
          Molecular
          <VariantDetailsFlagsIndicator
            :flag-state="flagsStore.flags.flag_molecular"
          />
        </div>
        <div class="col">
          Validation
          <VariantDetailsFlagsIndicator
            :flag-state="flagsStore.flags.flag_validation"
          />
        </div>
        <div class="col">
          Phenotype
          <VariantDetailsFlagsIndicator
            :flag-state="flagsStore.flags.flag_phenotype_match"
          />
        </div>
        <div class="col ml-1">
          <u>Summary</u>&nbsp;
          <VariantDetailsFlagsIndicator
            :flag-state="flagsStore.flags.flag_summary"
          />
        </div>
      </div>
    </div>
    <div class="col">
      <button
        class="btn btn-sm btn-primary pull-right"
        @click="setFlagsMode = true"
      >
        <i-fa-solid-flag />
        Edit
      </button>
    </div>
  </div>
  <div
    v-else-if="!flagsStore.flags && !setFlagsMode"
    class="row text-muted text-center p-2 pb-3"
  >
    <div class="col">
      <button
        class="btn btn-sm btn-primary pull-right"
        @click="setFlagsMode = true"
      >
        <i-fa-regular-flag />
        Add
      </button>
    </div>
  </div>
  <div v-else class="p-2">
    <div class="row">
      <div class="col">
        <div class="row">
          <div class="col-1 pl-0">
            <label for="flagBookmarked" title="bookmarked">
              <i-fa-solid-star />
            </label>
          </div>
          <div class="col-1 pl-1">
            <label for="flagForValidation" title="selected for validation">
              <i-fa-solid-flask />
            </label>
          </div>
          <div class="col-1 pl-1">
            <label for="flagCandidate" title="candidate variant">
              <i-fa-solid-heart />
            </label>
          </div>
          <div class="col-1 pl-1">
            <label for="flagFinalCausative" title="final causative/reported">
              <i-fa-solid-flag-checkered />
            </label>
          </div>
          <div class="col-1 pl-1">
            <label
              for="flagNoDiseaseAssociation"
              title="gene affected by this variant has no known disease association"
            >
              <i-cil-link-broken />
            </label>
          </div>
          <div class="col-1 pl-1">
            <label for="flagDoesSegregate" title="variant does segregate">
              <i-fa-solid-thumbs-up />
            </label>
          </div>
          <div class="col-1 pl-1">
            <label for="flagDoesntSegregate" title="variant doesn't segregate">
              <i-fa-solid-thumbs-down />
            </label>
          </div>
        </div>
        <div class="row">
          <div class="col-1 pl-0">
            <input
              type="checkbox"
              id="flagBookmarked"
              name="flag_bookmarked"
              v-model="flagsToSubmit.flag_bookmarked"
            />
          </div>
          <div class="col-1 pl-1">
            <input
              type="checkbox"
              id="flagForValidation"
              name="flag_for_validation"
              v-model="flagsToSubmit.flag_for_validation"
            />
          </div>
          <div class="col-1 pl-1">
            <input
              type="checkbox"
              id="flagCandidate"
              name="flag_candidate"
              v-model="flagsToSubmit.flag_candidate"
            />
          </div>
          <div class="col-1 pl-1">
            <input
              type="checkbox"
              id="flagFinalCausative"
              name="flag_final_causative"
              v-model="flagsToSubmit.flag_final_causative"
            />
          </div>
          <div class="col-1 pl-1">
            <input
              type="checkbox"
              id="flagNoDiseaseAssociation"
              name="flag_no_disease_association"
              v-model="flagsToSubmit.flag_no_disease_association"
            />
          </div>
          <div class="col-1 pl-1">
            <input
              type="checkbox"
              id="flagDoesSegregate"
              name="flag_segregates"
              v-model="flagsToSubmit.flag_segregates"
            />
          </div>
          <div class="col-1 pl-1">
            <input
              type="checkbox"
              id="flagDoesntSegregate"
              name="flag_doesnt_segregate"
              v-model="flagsToSubmit.flag_doesnt_segregate"
            />
          </div>
        </div>
      </div>
      <div class="col-8">
        <div class="row text-center">
          <div class="col">
            <label for="flagSelectorVisual">
              <strong>Visual</strong>
            </label>
          </div>
          <div class="col">
            <label for="flagSelectorMolecular">
              <strong>Molecular</strong>
            </label>
          </div>
          <div class="col">
            <label for="flagSelectorValidation">
              <strong>Validation</strong>
            </label>
          </div>
          <div class="col">
            <label for="flagSelectorPhenotype">
              <strong>Phenotype</strong>
            </label>
          </div>
          <div class="col">
            <label for="flagSelectorSummary">
              <strong><u>Summary</u></strong>
            </label>
          </div>
        </div>
        <div class="row">
          <div class="col">
            <select
              id="flagSelectorVisual"
              class="form-control form-control-sm"
              v-model="flagsToSubmit.flag_visual"
            >
              <option value="positive">positive</option>
              <option value="uncertain">uncertain</option>
              <option value="negative">negative</option>
              <option value="empty">empty</option>
            </select>
          </div>
          <div class="col">
            <select
              id="flagSelectorMolecular"
              class="form-control form-control-sm ml-2"
              v-model="flagsToSubmit.flag_molecular"
            >
              <option value="positive">positive</option>
              <option value="uncertain">uncertain</option>
              <option value="negative">negative</option>
              <option value="empty">empty</option>
            </select>
          </div>
          <div class="col">
            <select
              id="flagSelectorValidation"
              class="form-control form-control-sm ml-2"
              v-model="flagsToSubmit.flag_validation"
            >
              <option value="positive">positive</option>
              <option value="uncertain">uncertain</option>
              <option value="negative">negative</option>
              <option value="empty">empty</option>
            </select>
          </div>
          <div class="col">
            <select
              id="flagSelectorPhenotype"
              class="form-control form-control-sm ml-2"
              v-model="flagsToSubmit.flag_phenotype_match"
            >
              <option value="positive">positive</option>
              <option value="uncertain">uncertain</option>
              <option value="negative">negative</option>
              <option value="empty">empty</option>
            </select>
          </div>
          <div class="col">
            <select
              id="flagSelectorSummary"
              class="form-control form-control-sm ml-2"
              v-model="flagsToSubmit.flag_summary"
            >
              <option value="positive">positive</option>
              <option value="uncertain">uncertain</option>
              <option value="negative">negative</option>
              <option value="empty">empty</option>
            </select>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="btn-group pull-right">
          <button class="btn btn-sm btn-secondary" @click="cancelFlags()">
            Cancel
          </button>
          <button class="btn btn-sm btn-danger" @click="unsetFlags()">
            Clear
          </button>
          <button class="btn btn-sm btn-primary" @click="onSubmitFlags()">
            <i-fa-solid-flag />
            Submit
          </button>
        </div>
      </div>
    </div>
    <div class="row pt-2">
      <div class="col-7">
        <div
          class="alert alert-secondary small pull-left text-muted p-1 pl-2 pr-2"
        >
          <i-fa-solid-info-circle />
          Value in <strong><u>Summary</u></strong> will determine the row
          coloring in the results table. If <code>empty</code>, any other flag
          set except <i-fa-solid-star /> will color the row in gray (<i
            >&ldquo;work in progress&rdquo;</i
          >).
        </div>
      </div>
      <div class="col-5">
        <div
          class="alert alert-secondary small pull-right text-muted p-1 pl-2 pr-2"
        >
          <i-fa-solid-info-circle /> Press
          <span class="badge badge-danger">Clear</span> and
          <span class="badge badge-primary">Submit</span> to delete all flags.
        </div>
      </div>
    </div>
  </div>
</template>
