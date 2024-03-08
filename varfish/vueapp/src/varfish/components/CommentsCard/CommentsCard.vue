<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { DateTime } from 'luxon'

import { State } from '@varfish/storeUtils'
// import DocsLink from '@bihealth/reev-frontend-lib/components/DocsLink/DocsLink.vue'

/** This component's props. */
const props = defineProps<{
  commentsStore: any
  variant: any
  resultRowUuid: string
  caseUuid?: string
}>()

watch(
  () => [props.variant, props.caseUuid],
  () => {
    if (
      props.variant &&
      props.commentsStore.storeState.state === State.Active &&
      props.caseUuid
    ) {
      props.commentsStore.retrieveComments(props.variant, props.caseUuid)
    }
  },
)
onMounted(() => {
  if (props.variant && props.caseUuid) {
    props.commentsStore.retrieveComments(props.variant, props.caseUuid)
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

const setDeleteComment = (commentUuid: string, index: number) => {
  editCommentMode.value = EditCommentModes.Delete
  editCommentUuid.value = commentUuid
  editCommentIndex.value = index
}

const setEditComment = (commentUuid: string, text: string, index: number) => {
  editCommentMode.value = EditCommentModes.Edit
  editCommentUuid.value = commentUuid
  commentToSubmit.value = text
  editCommentIndex.value = index
}

const unsetEditComment = () => {
  editCommentMode.value = EditCommentModes.Off
  editCommentUuid.value = ''
  commentToSubmit.value = ''
  editCommentIndex.value = undefined
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
      props.resultRowUuid,
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
  <template v-else>
    <v-card>
      <v-card-title class="pb-0 pr-2">
        Comments
        <!-- <DocsLink anchor="flags" /> -->
      </v-card-title>
      <v-card-subtitle class="text-overline">
        View, create, or update comments
      </v-card-subtitle>
      <v-card-text>
        <template v-if="commentsStore.comments?.length">
          <v-sheet
            v-for="(comment, index) in commentsStore.comments"
            :key="`comment-${index}`"
            class="bg-grey-lighten-3 p-3"
            :class="{ 'mt-2': index > 0 }"
          >
            <v-row
              v-if="
                editCommentMode === EditCommentModes.Edit &&
                editCommentIndex === index
              "
              class="no-gutters flex-nowrap"
            >
              <v-col
                cols="10"
                class="flex-grow-0 pl-3"
                style="min-width: 100px; max-width: 100%"
              >
                <v-textarea
                  v-model="commentToSubmit"
                  variant="outlined"
                  rows="2"
                  label="Update comment text"
                  hide-details
                />
              </v-col>
              <v-col cols="2" class="flex-shrink-0">
                <v-btn-group
                  variant="tonal"
                  rounded="xs"
                  class="float-right mx-2"
                >
                  <v-btn @click="unsetEditComment()"> Cancel </v-btn>
                  <v-btn
                    color="primary"
                    :disabled="!commentToSubmit"
                    @click="onClickSubmitComment()"
                  >
                    Save
                  </v-btn>
                </v-btn-group>
              </v-col>
            </v-row>
            <v-row
              v-else-if="
                editCommentMode === EditCommentModes.Delete &&
                editCommentIndex === index
              "
              class="no-gutters flex-nowrap"
            >
              <v-col cols="10" class="ml-2">
                <div>
                  <span class="text-grey-darken-1">#{{ index + 1 }}</span>
                  &nbsp;
                  <span class="font-bolder">{{ comment.user }}</span>
                  <span class="font-italic"
                    >@{{
                      DateTime.fromISO(comment.date_created).toFormat(
                        'yyyy/MM/dd hh:mm',
                      )
                    }}</span
                  >
                </div>
                <div>
                  {{ comment.text }}
                </div>
              </v-col>
              <v-col cols="2">
                <v-btn-group
                  variant="tonal"
                  rounded="xs"
                  density="compact"
                  class="float-right mx-2"
                >
                  <v-btn @click="unsetEditComment()"> Cancel </v-btn>
                  <v-btn color="error" @click="onClickDeleteComment()">
                    Delete
                  </v-btn>
                </v-btn-group>
              </v-col>
            </v-row>
            <div v-else-if="comment">
              <v-btn-group
                divided
                variant="outlined"
                rounded="xs"
                density="compact"
                class="float-right"
              >
                <v-btn
                  size="default"
                  icon="mdi-pencil"
                  @click="
                    setEditComment(comment.sodar_uuid, comment.text, index)
                  "
                />
                <v-btn
                  size="default"
                  icon="mdi-delete"
                  @click="setDeleteComment(comment.sodar_uuid, index)"
                />
              </v-btn-group>
              <div>
                <span class="text-grey-darken-1">#{{ index + 1 }}</span> &nbsp;
                <span class="font-bolder">{{ comment.user }}</span>
                <span class="font-italic"
                  >@{{
                    DateTime.fromISO(comment.date_created).toFormat(
                      'yyyy/MM/dd hh:mm',
                    )
                  }}</span
                >
              </div>
              <div>
                {{ comment.text }}
              </div>
            </div>
            <div v-else class="text-center text-muted font-italic">
              Comment has been deleted.
            </div>
          </v-sheet>
        </template>
        <div v-else>
          <p class="text-muted text-center font-italic">No comments yet.</p>
        </div>
      </v-card-text>
      <v-card-text v-if="editCommentMode === EditCommentModes.Off">
        <v-textarea
          v-model="commentToSubmit"
          hide-details
          variant="outlined"
          label="Comment Text"
          prepend-icon="mdi-comment-outline"
          class="mb-3"
        >
        </v-textarea>
        <v-row>
          <v-col cols="12" class="text-center">
            <v-btn
              variant="outlined"
              prepend-icon="mdi-close-circle-outline"
              rounded="xs"
              class="mr-3"
              @click="commentToSubmit = ''"
            >
              Clear
            </v-btn>
            <v-btn
              variant="tonal"
              prepend-icon="mdi-cloud-upload"
              rounded="xs"
              :disabled="!commentToSubmit"
              @click="onClickSubmitComment()"
            >
              Submit
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-text v-else class="text-center text-muted font-italic">
        <v-icon>mdi-information-outline</v-icon>
        The form for placing comments will reappear when you finish/cancel
        editing your comment.
      </v-card-text>
    </v-card>
  </template>
</template>

<style>
label.v-label {
  margin-bottom: 0;
}
</style>
