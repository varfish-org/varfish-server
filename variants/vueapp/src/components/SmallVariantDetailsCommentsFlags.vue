<script setup>
import { useVariantDetailsStore } from '@variants/stores/variantDetails'
import { useFilterQueryStore } from '@variants/stores/filterQuery'
import { EditCommentModes } from '@variants/enums'
import SmallVariantDetailsCommentsFlagsIndicator from './SmallVariantDetailsCommentsFlagsIndicator.vue'

const detailsStore = useVariantDetailsStore()
const queryStore = useFilterQueryStore()

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
    v-if="detailsStore.flags && !detailsStore.setFlagsMode"
    class="row font-weight-bold p-2"
  >
    <div class="col">
      <div class="row">
        <div class="col-1 pl-0">
          <i-fa-solid-star
            :class="displayMutedIfFalse(detailsStore.flags.flag_bookmarked)"
            :style="displayOpacityIfFalse(detailsStore.flags.flag_bookmarked)"
          />
        </div>
        <div class="col-1 pl-1">
          <i-fa-solid-flask
            :class="displayMutedIfFalse(detailsStore.flags.flag_for_validation)"
            :style="
              displayOpacityIfFalse(detailsStore.flags.flag_for_validation)
            "
          />
        </div>
        <div class="col-1 pl-1">
          <i-fa-solid-heart
            class="ml-1"
            :class="displayMutedIfFalse(detailsStore.flags.flag_candidate)"
            :style="displayOpacityIfFalse(detailsStore.flags.flag_candidate)"
          />
        </div>
        <div class="col-1 pl-1">
          <i-fa-solid-flag-checkered
            class="ml-1"
            :class="
              displayMutedIfFalse(detailsStore.flags.flag_final_causative)
            "
            :style="
              displayOpacityIfFalse(detailsStore.flags.flag_final_causative)
            "
            data-icon="fa-solid:flag-checkered"
          />
        </div>
        <div class="col-1 pl-1">
          <i-cil-link-broken
            class="ml-1"
            :class="
              displayMutedIfFalse(
                detailsStore.flags.flag_no_disease_association
              )
            "
            :style="
              displayOpacityIfFalse(
                detailsStore.flags.flag_no_disease_association
              )
            "
          />
        </div>
        <div class="col-1 pl-1">
          <i-fa-solid-thumbs-up
            class="ml-1"
            :class="displayMutedIfFalse(detailsStore.flags.flag_segregates)"
            :style="displayOpacityIfFalse(detailsStore.flags.flag_segregates)"
          />
        </div>
        <div class="col-1 pl-1">
          <i-fa-solid-thumbs-down
            class="ml-1"
            :class="
              displayMutedIfFalse(detailsStore.flags.flag_doesnt_segregate)
            "
            :style="
              displayOpacityIfFalse(detailsStore.flags.flag_doesnt_segregate)
            "
          />
        </div>
      </div>
    </div>
    <div class="col-8">
      <div class="row text-center">
        <div class="col">
          Visual
          <SmallVariantDetailsCommentsFlagsIndicator
            :flag-state="detailsStore.flags.flag_visual"
          />
        </div>
        <div class="col">
          Molecular
          <SmallVariantDetailsCommentsFlagsIndicator
            :flag-state="detailsStore.flags.flag_molecular"
          />
        </div>
        <div class="col">
          Validation
          <SmallVariantDetailsCommentsFlagsIndicator
            :flag-state="detailsStore.flags.flag_validation"
          />
        </div>
        <div class="col">
          Phenotype
          <SmallVariantDetailsCommentsFlagsIndicator
            :flag-state="detailsStore.flags.flag_phenotype_match"
          />
        </div>
        <div class="col ml-1">
          <u>Summary</u>&nbsp;
          <SmallVariantDetailsCommentsFlagsIndicator
            :flag-state="detailsStore.flags.flag_summary"
          />
        </div>
      </div>
    </div>
    <div class="col">
      <button
        class="btn btn-sm btn-primary pull-right"
        @click="detailsStore.setFlagsMode = true"
      >
        <i-fa-solid-flag />
        Edit
      </button>
    </div>
  </div>
  <div
    v-else-if="!detailsStore.flags && !detailsStore.setFlagsMode"
    class="row text-muted text-center p-2 pb-3"
  >
    <div class="col">
      <button
        class="btn btn-sm btn-primary pull-right"
        @click="detailsStore.setFlagsMode = true"
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
              v-model="detailsStore.flagsToSubmit.flag_bookmarked"
            />
          </div>
          <div class="col-1 pl-1">
            <input
              type="checkbox"
              id="flagForValidation"
              name="flag_for_validation"
              v-model="detailsStore.flagsToSubmit.flag_for_validation"
            />
          </div>
          <div class="col-1 pl-1">
            <input
              type="checkbox"
              id="flagCandidate"
              name="flag_candidate"
              v-model="detailsStore.flagsToSubmit.flag_candidate"
            />
          </div>
          <div class="col-1 pl-1">
            <input
              type="checkbox"
              id="flagFinalCausative"
              name="flag_final_causative"
              v-model="detailsStore.flagsToSubmit.flag_final_causative"
            />
          </div>
          <div class="col-1 pl-1">
            <input
              type="checkbox"
              id="flagNoDiseaseAssociation"
              name="flag_no_disease_association"
              v-model="detailsStore.flagsToSubmit.flag_no_disease_association"
            />
          </div>
          <div class="col-1 pl-1">
            <input
              type="checkbox"
              id="flagDoesSegregate"
              name="flag_segregates"
              v-model="detailsStore.flagsToSubmit.flag_segregates"
            />
          </div>
          <div class="col-1 pl-1">
            <input
              type="checkbox"
              id="flagDoesntSegregate"
              name="flag_doesnt_segregate"
              v-model="detailsStore.flagsToSubmit.flag_doesnt_segregate"
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
              v-model="detailsStore.flagsToSubmit.flag_visual"
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
              v-model="detailsStore.flagsToSubmit.flag_molecular"
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
              v-model="detailsStore.flagsToSubmit.flag_validation"
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
              v-model="detailsStore.flagsToSubmit.flag_phenotype_match"
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
              v-model="detailsStore.flagsToSubmit.flag_summary"
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
          <button
            class="btn btn-sm btn-secondary"
            @click="detailsStore.cancelFlags()"
          >
            Cancel
          </button>
          <button
            class="btn btn-sm btn-danger"
            @click="detailsStore.unsetFlags()"
          >
            Clear
          </button>
          <button
            class="btn btn-sm btn-primary"
            @click="detailsStore.submitFlags(queryStore.csrfToken)"
          >
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
  <div class="card">
    <ul
      v-if="detailsStore.comments.length > 0"
      class="list-group list-group-flush list"
    >
      <li
        v-for="(comment, index) in detailsStore.comments"
        :key="index"
        class="list-group-item list-item p-4"
      >
        <div
          v-if="
            detailsStore.editCommentMode === EditCommentModes.Edit &&
            detailsStore.editCommentIndex === index
          "
          class="input-group form-inline"
        >
          <textarea
            rows="1"
            cols="40"
            class="form-control"
            v-model="detailsStore.commentToSubmit"
          ></textarea>
          <span class="btn-group pull-right">
            <button
              type="button"
              class="btn btn-sm btn-secondary"
              @click="detailsStore.unsetEditComment()"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-sm btn-primary"
              @click="detailsStore.submitComment(queryStore.csrfToken)"
              :disabled="!detailsStore.commentToSubmit"
            >
              Submit
            </button>
          </span>
        </div>
        <div
          v-else-if="
            detailsStore.editCommentMode === EditCommentModes.Delete &&
            detailsStore.editCommentIndex === index
          "
        >
          <span class="small text-muted">
            <strong>{{ comment.user }}</strong>
            {{ comment.date_created }}:
          </span>
          <em>{{ comment.text }}</em>
          <span class="btn-group pull-right">
            <button
              type="button"
              class="btn btn-sm btn-secondary"
              @click="detailsStore.unsetEditComment()"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-sm btn-danger"
              @click="detailsStore.deleteComment(queryStore.csrfToken)"
            >
              Delete
            </button>
          </span>
        </div>
        <div v-else-if="comment">
          <span class="small text-muted">
            <strong>{{ comment.user }}</strong>
            {{ comment.date_created }}:
          </span>
          <em>{{ comment.text }}</em>
          <div class="btn-group pull-right" v-if="comment.user_can_edit">
            <button
              class="btn btn-sm btn-outline-secondary"
              @click="
                detailsStore.setEditComment(
                  comment.sodar_uuid,
                  comment.text,
                  index
                )
              "
            >
              <i-mdi-pencil />
            </button>
            <button
              class="btn btn-sm btn-outline-secondary"
              @click="detailsStore.setDeleteComment(comment.sodar_uuid, index)"
            >
              <i-fa-solid-times-circle />
            </button>
          </div>
        </div>
        <div v-else>
          <i class="text-muted">Comment has been deleted.</i>
        </div>
      </li>
    </ul>
    <div v-else class="card-body">
      <p class="text-muted font-italic text-center">
        <i-fa-solid-info-circle />
        No comments.
      </p>
    </div>
    <div
      class="card-footer"
      v-if="detailsStore.editCommentMode === EditCommentModes.Off"
    >
      <textarea
        v-model="detailsStore.commentToSubmit"
        class="form-control"
        placeholder="Comment variant here ..."
      ></textarea>
      <div class="btn-group">
        <button
          class="btn btn-secondary"
          @click="detailsStore.commentToSubmit = ''"
        >
          Clear
        </button>
        <button
          class="btn btn-primary"
          @click="detailsStore.submitComment(queryStore.csrfToken)"
          :disabled="!detailsStore.commentToSubmit"
        >
          Submit
        </button>
      </div>
    </div>
    <div class="card-footer" v-else>
      <i class="text-muted">
        <i-fa-solid-info-circle />
        The form for placing comments will appear when you finished editing your
        comment.
      </i>
    </div>
  </div>
</template>
