<template>
  <div
    v-if="detailsStore.flags && !detailsStore.setFlagsMode"
    class="row font-weight-bold p-2"
  >
    <div class="col">
      <div class="row">
        <div class="col-1 pl-0">
          <i
            class="iconify"
            :class="
              $filters.displayMutedIfFalse(detailsStore.flags.flag_bookmarked)
            "
            :style="
              $filters.displayOpacityIfFalse(detailsStore.flags.flag_bookmarked)
            "
            data-icon="fa-solid:star"
          ></i>
        </div>
        <div class="col-1 pl-1">
          <i
            class="iconify ml-1"
            :class="
              $filters.displayMutedIfFalse(
                detailsStore.flags.flag_for_validation
              )
            "
            :style="
              $filters.displayOpacityIfFalse(
                detailsStore.flags.flag_for_validation
              )
            "
            data-icon="fa-solid:flask"
          ></i>
        </div>
        <div class="col-1 pl-1">
          <i
            class="iconify ml-1"
            :class="
              $filters.displayMutedIfFalse(detailsStore.flags.flag_candidate)
            "
            :style="
              $filters.displayOpacityIfFalse(detailsStore.flags.flag_candidate)
            "
            data-icon="fa-solid:heart"
          ></i>
        </div>
        <div class="col-1 pl-1">
          <i
            class="iconify ml-1"
            :class="
              $filters.displayMutedIfFalse(
                detailsStore.flags.flag_final_causative
              )
            "
            :style="
              $filters.displayOpacityIfFalse(
                detailsStore.flags.flag_final_causative
              )
            "
            data-icon="fa-solid:flag-checkered"
          ></i>
        </div>
        <div class="col-1 pl-1">
          <i
            class="iconify ml-1"
            :class="
              $filters.displayMutedIfFalse(
                detailsStore.flags.flag_no_disease_association
              )
            "
            :style="
              $filters.displayOpacityIfFalse(
                detailsStore.flags.flag_no_disease_association
              )
            "
            data-icon="cil:link-broken"
          ></i>
        </div>
        <div class="col-1 pl-1">
          <i
            class="iconify ml-1"
            :class="
              $filters.displayMutedIfFalse(detailsStore.flags.flag_segregates)
            "
            :style="
              $filters.displayOpacityIfFalse(detailsStore.flags.flag_segregates)
            "
            data-icon="fa-solid:thumbs-up"
          ></i>
        </div>
        <div class="col-1 pl-1">
          <i
            class="iconify ml-1"
            :class="
              $filters.displayMutedIfFalse(
                detailsStore.flags.flag_doesnt_segregate
              )
            "
            :style="
              $filters.displayOpacityIfFalse(
                detailsStore.flags.flag_doesnt_segregate
              )
            "
            data-icon="fa-solid:thumbs-down"
          ></i>
        </div>
      </div>
    </div>
    <div class="col-8">
      <div class="row text-center">
        <div class="col">
          Visual
          <i
            class="iconify ml-1"
            style="font-size: 1.2em"
            :class="$filters.displayFlagColor(detailsStore.flags.flag_visual)"
            :data-icon="
              $filters.displayFlagIcon(detailsStore.flags.flag_visual)
            "
          ></i>
        </div>
        <div class="col">
          Molecular
          <i
            class="iconify ml-1"
            style="font-size: 1.2em"
            :class="
              $filters.displayFlagColor(detailsStore.flags.flag_molecular)
            "
            :data-icon="
              $filters.displayFlagIcon(detailsStore.flags.flag_molecular)
            "
          ></i>
        </div>
        <div class="col">
          Validation
          <i
            class="iconify ml-1"
            style="font-size: 1.2em"
            :class="
              $filters.displayFlagColor(detailsStore.flags.flag_validation)
            "
            :data-icon="
              $filters.displayFlagIcon(detailsStore.flags.flag_validation)
            "
          ></i>
        </div>
        <div class="col">
          Phenotype
          <i
            class="iconify ml-1"
            style="font-size: 1.2em"
            :class="
              $filters.displayFlagColor(detailsStore.flags.flag_phenotype_match)
            "
            :data-icon="
              $filters.displayFlagIcon(detailsStore.flags.flag_phenotype_match)
            "
          ></i>
        </div>
        <div class="col ml-1">
          <u>Summary</u>&nbsp;
          <i
            class="iconify"
            style="font-size: 1.2em"
            :class="$filters.displayFlagColor(detailsStore.flags.flag_summary)"
            :data-icon="
              $filters.displayFlagIcon(detailsStore.flags.flag_summary)
            "
          ></i>
        </div>
      </div>
    </div>
    <div class="col">
      <button
        class="btn btn-sm btn-primary pull-right"
        @click="detailsStore.setFlagsMode = true"
      >
        <i class="iconify" data-icon="fa-solid:flag"></i>
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
        <i class="iconify" data-icon="fa-regular:flag"></i>
        Add
      </button>
    </div>
  </div>
  <div v-else class="p-2">
    <div class="row">
      <div class="col">
        <div class="row">
          <div class="col-1 pl-0">
            <label for="flagBookmarked" title="bookmarked"
              ><i class="iconify" data-icon="fa-solid:star"></i
            ></label>
          </div>
          <div class="col-1 pl-1">
            <label for="flagForValidation" title="selected for validation"
              ><i class="iconify" data-icon="fa-solid:flask"></i
            ></label>
          </div>
          <div class="col-1 pl-1">
            <label for="flagCandidate" title="candidate variant"
              ><i class="iconify" data-icon="fa-solid:heart"></i
            ></label>
          </div>
          <div class="col-1 pl-1">
            <label for="flagFinalCausative" title="final causative/reported"
              ><i class="iconify" data-icon="fa-solid:flag-checkered"></i
            ></label>
          </div>
          <div class="col-1 pl-1">
            <label
              for="flagNoDiseaseAssociation"
              title="gene affected by this variant has no known disease association"
              ><i class="iconify" data-icon="cil:link-broken"></i
            ></label>
          </div>
          <div class="col-1 pl-1">
            <label for="flagDoesSegregate" title="variant does segregate"
              ><i class="iconify" data-icon="fa-solid:thumbs-up"></i
            ></label>
          </div>
          <div class="col-1 pl-1">
            <label for="flagDoesntSegregate" title="variant doesn't segregate"
              ><i class="iconify" data-icon="fa-solid:thumbs-down"></i
            ></label>
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
            <i class="iconify" data-icon="fa-solid:flag"></i>
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
          <i class="iconify" data-icon="fa-solid:info-circle"></i>
          Value in <strong><u>Summary</u></strong> will determine the row
          coloring in the results table. If <code>empty</code>, any other flag
          set except <i class="iconify" data-icon="fa-solid:star"></i> will
          color the row in gray (<i>&ldquo;work in progress&rdquo;</i>).
        </div>
      </div>
      <div class="col-5">
        <div
          class="alert alert-secondary small pull-right text-muted p-1 pl-2 pr-2"
        >
          <i class="iconify" data-icon="fa-solid:info-circle"></i> Press
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
              <i class="iconify" data-icon="mdi:pencil"></i>
            </button>
            <button
              class="btn btn-sm btn-outline-secondary"
              @click="detailsStore.setDeleteComment(comment.sodar_uuid, index)"
            >
              <i class="iconify" data-icon="fa-solid:times-circle"></i>
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
        <i class="iconify" data-icon="fa-solid:info-circle"></i> No comments.
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
      <i class="text-muted"
        ><i class="iconify" data-icon="fa-solid:info-circle"></i> The form for
        placing comments will appear when you finished editing your comment.</i
      >
    </div>
  </div>
</template>

<script>
import { variantDetailsStore } from '@variants/stores/variantDetails'
import { filterQueryStore } from '@variants/stores/filterQuery'
import { EditCommentModes } from '@variants/enums'

export default {
  components: {},
  setup() {
    const detailsStore = variantDetailsStore()
    const queryStore = filterQueryStore()
    return {
      detailsStore,
      queryStore,
      EditCommentModes,
    }
  },
}
</script>
