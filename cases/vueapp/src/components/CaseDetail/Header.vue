<script setup>
import { useRouter } from 'vue-router'

import { useCaseListStore } from '@cases/stores/caseList'
import UiToggleMaxButton from '@varfish/components/UiToggleMaxButton/UiToggleMaxButton.vue'

/** Define props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  // eslint-disable-next-line vue/require-default-prop
  caseObj: Object,
})

/** Define emits. */
const emit = defineEmits([
  'addCaseCommentClick',
  'editCaseStatusClick',
  'editCaseNotesClick',
  'editQueryPresetsClick',
  'editPedigreeClick',
  'destroyCaseClick',
])

/** The currently used router. */
const router = useRouter()

const caseListStore = useCaseListStore()

const userHasPerms = (perm) =>
  caseListStore.userPerms && caseListStore.userPerms.includes(perm)
</script>

<template>
  <div>
    <!-- title etc. -->
    <div class="row sodar-pr-content-title pb-1">
      <!-- TODO buttons from sodar core -->
      <h2 class="sodar-pr-content-title">
        Case
        <small v-if="caseObj" class="text-muted">{{ caseObj.name }}</small>
        <small v-else>NO CASE</small>

        <a
          id="sodar-pr-btn-copy-uuid"
          role="submit"
          class="btn btn-link mr-2 sodar-pr-btn-title sodar-pr-btn-copy-uuid sodar-copy-btn"
          :data-clipboard-text="caseObj ? caseObj.sodar_uuid : ''"
          title="Copy UUID to clipboard"
          data-toggle="tooltip"
          data-placement="top"
        >
          <i-fa-solid-clipboard class="text-muted" />
        </a>
      </h2>

      <div class="ml-auto btn-group">
        <a class="btn btn-secondary" @click.prevent="router.push('/')">
          <i-mdi-arrow-left-circle />
          Back to Project
        </a>
        <a
          class="btn btn-primary"
          @click.prevent="
            router.push({
              name: 'variants-filter',
              params: { case: caseObj.sodar_uuid },
            })
          "
        >
          <i-mdi-filter />
          Filter Variants
        </a>
        <a
          class="btn btn-primary"
          @click.prevent="
            router.push({
              name: 'svs-filter',
              params: { case: caseObj.sodar_uuid },
            })
          "
        >
          <i-mdi-filter-variant />
          Filter SVs
        </a>
        <UiToggleMaxButton />
        <template v-if="userHasPerms('cases.update_case')">
          <a
            type="button"
            class="btn btn-secondary dropdown-toggle"
            data-toggle="dropdown"
          >
            <i-mdi-cog />
          </a>
          <div class="dropdown-menu">
            <a
              class="dropdown-item"
              href="#"
              @click.prevent="emit('editQueryPresetsClick')"
            >
              <i-mdi-filter-settings />
              Edit Query Presets
            </a>
            <a
              class="dropdown-item"
              href="#"
              @click.prevent="emit('addCaseCommentClick')"
            >
              <i-mdi-comment-plus />
              Add Comment
            </a>
            <a
              class="dropdown-item"
              href="#"
              @click.prevent="emit('editCaseStatusClick')"
            >
              <i-mdi-square-edit-outline />
              Edit Status
            </a>
            <a
              class="dropdown-item"
              href="#"
              @click.prevent="emit('editCaseNotesClick')"
            >
              <i-mdi-playlist-edit />
              Edit Notes
            </a>
            <a
              class="dropdown-item"
              href="#"
              @click.prevent="emit('editPedigreeClick')"
            >
              <i-mdi-file-document-edit />
              Edit Pedigree
            </a>
            <a class="dropdown-item" href="#">
              <i-mdi-gender-male-female />
              Fix Sex
            </a>
            <a
              v-if="userHasPerms('cases.delete_case')"
              class="dropdown-item text-danger"
              href="#"
              @click.prevent="emit('destroyCaseClick')"
            >
              <i-mdi-delete-forever />
              Delete Case
            </a>
          </div>
        </template>
      </div>
    </div>

    <!-- inline help -->
    <div
      v-if="caseListStore.showInlineHelp"
      class="alert alert-secondary small p-2"
    >
      <i-mdi-information />
      This is the case detail view. Here, you can inspect the case and its
      properties and perform edit operations on the case.
    </div>
  </div>
</template>
