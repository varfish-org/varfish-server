<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'

import { State } from '@varfish/storeUtils'
import Overlay from '@varfish/components/Overlay.vue'

/** This component's props. */
const props = defineProps<{
  commentsStore: any
  variant: any
}>()

/** Whether to show the overlay. */
const overlayShow = computed(
  () => (props.commentsStore?.serverInteractions ?? 0) > 0,
)

watch(
  () => props.variant,
  () => {
    if (
      props.variant &&
      props.commentsStore.storeState.state === State.Active
    ) {
      props.commentsStore.retrieveComments(props.variant)
    }
  },
)
onMounted(() => {
  if (props.variant) {
    props.commentsStore.retrieveComments(props.variant)
  }
})

enum EditCommentModes {
  Off = 0,
  Edit = 1,
  Delete = 2,
}

const commentToSubmit = ref<string>('')
const editCommentMode = ref<EditCommentModes>(EditCommentModes.Off)
const editCommentUuid = ref<string>('')
const editCommentIndex = ref<number | undefined>(undefined)

const setDeleteComment = (commentUuid, index) => {
  editCommentMode.value = EditCommentModes.Delete
  editCommentUuid.value = commentUuid
  editCommentIndex.value = index
}

const setEditComment = (commentUuid, text, index) => {
  editCommentMode.value = EditCommentModes.Edit
  editCommentUuid.value = commentUuid
  commentToSubmit.value = text
  editCommentIndex.value = index
}

const unsetEditComment = () => {
  editCommentMode.value = EditCommentModes.Off
  editCommentUuid.value = ''
  commentToSubmit.value = ''
  editCommentIndex.value = null
}

const onClickSubmitComment = async () => {
  if (editCommentMode.value === EditCommentModes.Edit) {
    await props.commentsStore.updateComment(
      editCommentUuid.value,
      commentToSubmit.value,
    )
  } else {
    await props.commentsStore.createComment(
      props.variant,
      commentToSubmit.value,
    )
  }
  unsetEditComment()
}

const onClickDeleteComment = async () => {
  if (editCommentUuid.value) {
    await props.commentsStore.deleteComment(editCommentUuid.value)
  }
  commentToSubmit.value = ''
  editCommentMode.value = EditCommentModes.Off
  editCommentUuid.value = ''
}

// Reset comment editor state when the small variant changes.
watch(
  () => props.variant,
  (_newValue, _oldValue) => {
    commentToSubmit.value = ''
    editCommentMode.value = EditCommentModes.Off
    editCommentUuid.value = ''
  },
)
</script>

<template>
  <!-- missing data => display loader-->
  <template v-if="!(commentsStore && variant)">
    <v-skeleton-loader
      class="mt-3 mx-auto border"
      type="heading,subtitle,text,text"
    />
  </template>
  <!-- otherwise, display actual card -->
  <template v-else> </template>
  <div
    class="varfish-overlay-wrap position-relative flex-grow-1 d-flex flex-column"
  >
    <div>
      <ul
        v-if="commentsStore.comments?.length"
        class="list-group list-group-flush list"
      >
        <li
          v-for="(comment, index) in commentsStore.comments"
          :key="index"
          class="list-group-item list-item p-4"
        >
          <div
            v-if="
              editCommentMode === EditCommentModes.Edit &&
              editCommentIndex === index
            "
            class="input-group form-inline"
          >
            <textarea
              rows="1"
              cols="40"
              class="form-control"
              v-model="commentToSubmit"
            ></textarea>
            <span class="btn-group pull-right">
              <button
                type="button"
                class="btn btn-sm btn-secondary"
                @click="unsetEditComment()"
              >
                Cancel
              </button>
              <button
                type="button"
                class="btn btn-sm btn-primary"
                @click="onClickSubmitComment()"
                :disabled="!commentToSubmit"
              >
                Submit
              </button>
            </span>
          </div>
          <div
            v-else-if="
              editCommentMode === EditCommentModes.Delete &&
              editCommentIndex === index
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
                @click="unsetEditComment()"
              >
                Cancel
              </button>
              <button
                type="button"
                class="btn btn-sm btn-danger"
                @click="onClickDeleteComment()"
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
                @click="setEditComment(comment.sodar_uuid, comment.text, index)"
              >
                <i-mdi-pencil />
              </button>
              <button
                class="btn btn-sm btn-outline-secondary"
                @click="setDeleteComment(comment.sodar_uuid, index)"
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
        class="card-footer pl-2 pr-2 text-right"
        v-if="editCommentMode === EditCommentModes.Off"
      >
        <textarea
          v-model="commentToSubmit"
          class="form-control mb-2"
          placeholder="Comment variant here ..."
        ></textarea>
        <div class="btn-group ml-auto mb-2">
          <button class="btn btn-secondary" @click="commentToSubmit = ''">
            Clear
          </button>
          <button
            class="btn btn-primary"
            @click="onClickSubmitComment()"
            :disabled="!commentToSubmit"
          >
            Submit
          </button>
        </div>
      </div>
      <div class="card-footer" v-else>
        <i class="text-muted">
          <i-fa-solid-info-circle />
          The form for placing comments will appear when you finished editing
          your comment.
        </i>
      </div>
    </div>
    <Overlay v-if="overlayShow" />
  </div>
</template>

<style>
label.v-label {
  margin-bottom: 0;
}
</style>
