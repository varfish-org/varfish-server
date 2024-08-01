<script setup lang="ts">
import { useCaseListStore } from '@/cases/stores/caseList'
import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import TheNavBar from '@/cases/components/TheNavBar/TheNavBar.vue'
import CaseDetailPane from './CaseDetailPane.vue'
import { ref } from 'vue'

const paneRef = ref<typeof CaseDetailPane | undefined>(undefined)

const props = defineProps<{
  /** The project UUID. */
  projectUuid: string
  /** The case UUID. */
  caseUuid: string
  /** The current tab. */
  currentTab: string
}>()

const caseListStore = useCaseListStore()

// Whether to hide the navigation bar; component state.
const navbarHidden = ref<boolean>(false)

const userHasPerms = (perm: string) =>
  caseListStore.userPerms && caseListStore.userPerms.includes(perm)
</script>

<template>
  <v-app id="case-detail">
    <TheAppBar v-model:navbar-hidden="navbarHidden" />
    <TheNavBar :navbar-hidden="navbarHidden">
      <v-list-item
        prepend-icon="mdi-arrow-left"
        :to="{
          name: 'case-list',
          params: { project: props.projectUuid },
        }"
      >
        <template v-if="!navbarHidden"> Back to Case List </template>
      </v-list-item>
      <v-list-subheader class="text-uppercase">
        Case Overview
      </v-list-subheader>
      <v-list-item
        prepend-icon="mdi-account"
        :to="{
          name: 'case-detail-overview',
          params: { project: projectUuid, case: caseUuid },
        }"
      >
        Overview
      </v-list-item>
      <v-list-item
        prepend-icon="mdi-chart-multiple"
        :to="{
          name: 'case-detail-qc',
          params: { project: projectUuid, case: caseUuid },
        }"
      >
        Quality Control
      </v-list-item>
      <v-list-item
        prepend-icon="mdi-bookmark-multiple"
        :to="{
          name: 'case-detail-annotation',
          params: { project: projectUuid, case: caseUuid },
        }"
      >
        Variant Annotation
      </v-list-item>

      <v-list-subheader class="text-uppercase">
        Variant Analysis
      </v-list-subheader>

      <v-list-item
        prepend-icon="mdi-filter"
        append-icon="mdi-arrow-right"
        :to="{
          name: 'variants-filter',
          params: { case: caseUuid },
        }"
      >
        Filter Variants
      </v-list-item>
      <v-list-item
        prepend-icon="mdi-filter-variant"
        append-icon="mdi-arrow-right"
        :to="{
          name: 'svs-filter',
          params: { case: caseUuid },
        }"
      >
        Filter SVs
      </v-list-item>

      <template v-if="userHasPerms('cases.update_case')">
        <v-list-subheader class="text-uppercase">
          Case Operations
        </v-list-subheader>

        <v-list-item
          prepend-icon="mdi-filter-settings"
          link
          @click="paneRef!.handleEditQueryPresetsClicked()"
        >
          Edit Query Presets
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-comment-plus"
          link
          @click="paneRef!.handleAddCaseCommentClicked()"
        >
          Add Comment
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-square-edit-outline"
          link
          @click="paneRef!.handleEditCaseStatusClicked()"
        >
          Edit Status
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-playlist-edit"
          link
          @click="paneRef!.handleEditCaseNotesClicked()"
        >
          Edit Notes
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-file-document-edit"
          link
          @click="paneRef!.handleEditPedigreeClicked()"
        >
          Edit Pedigree
        </v-list-item>
        <v-list-item
          v-if="userHasPerms('cases.delete_case')"
          prepend-icon="mdi-delete-forever"
          link
          base-color="error"
          class="dropdown-item text-danger"
          @click="paneRef!.handleDestroyCaseClicked()"
        >
          Delete Case
        </v-list-item>
      </template>
    </TheNavBar>
    <div class="pa-3">
      <v-main>
        <CaseDetailPane
          ref="paneRef"
          :project-uuid="props.projectUuid"
          :case-uuid="props.caseUuid"
          :current-tab="props.currentTab"
        />
      </v-main>
    </div>
  </v-app>
</template>
