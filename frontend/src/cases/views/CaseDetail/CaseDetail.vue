<script setup lang="ts">
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { useCaseListStore } from '@/cases/stores/caseList'
import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import TheNavBar from '@/cases/components/TheNavBar/TheNavBar.vue'
import CaseDetailPane from './CaseDetailPane.vue'
import { onBeforeMount, ref, watch } from 'vue'

const paneRef = ref<typeof CaseDetailPane | undefined>(undefined)

const props = defineProps<{
  /** The project UUID. */
  projectUuid: string
  /** The case UUID. */
  caseUuid: string
  /** The current tab. */
  currentTab: string
}>()

const caseDetailsStore = useCaseDetailsStore()
const caseListStore = useCaseListStore()

/** Whether to hide the navigation bar; component state. */
const navbarHidden = ref<boolean>(false)

/** Returns whether the user has the given permissions. */
const userHasPerms = (perm: string) =>
  caseListStore.userPerms && caseListStore.userPerms.includes(perm)

/** Refresh the stores. */
const refreshStores = async () => {
  if (!props.caseUuid) {
    return
  }
  await caseDetailsStore.initialize(props.projectUuid, props.caseUuid)
}

// Initialize (=refresh) stores when mounted.
onBeforeMount(async () => refreshStores())

// Refresh stores when the case UUID changes.
watch(
  () => props.caseUuid,
  async () => refreshStores(),
)
</script>

<template>
  <v-app id="case-detail">
    <TheAppBar
      :show-left-panel-button="true"
      :show-right-panel-button="false"
      v-model:hide-left-panel="navbarHidden"
    />
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
      <v-list-subheader v-if="!navbarHidden" class="text-uppercase">
        Case Overview
      </v-list-subheader>
      <v-list-item
        :class="{ 'pt-3 mt-1 border-t-thin': navbarHidden }"
        prepend-icon="mdi-account"
        :to="{
          name: 'case-detail-overview',
          params: { project: projectUuid, case: caseUuid },
        }"
      >
        <template v-if="!navbarHidden"> Overview </template>
      </v-list-item>
      <v-list-item
        prepend-icon="mdi-chart-multiple"
        :to="{
          name: 'case-detail-qc',
          params: { project: projectUuid, case: caseUuid },
        }"
      >
        <template v-if="!navbarHidden"> Quality Control </template>
      </v-list-item>
      <v-list-item
        prepend-icon="mdi-bookmark-multiple"
        :to="{
          name: 'case-detail-annotation',
          params: { project: projectUuid, case: caseUuid },
        }"
      >
        <template v-if="!navbarHidden"> Variant Annotation </template>
      </v-list-item>

      <template v-if="!caseDetailsStore.caseObj">
        <v-list-subheader class="text-uppercase" v-if="!navbarHidden">
          Variant Analysis
        </v-list-subheader>
        <v-skeleton-loader
          loading
          type="list-item, list-item"
          class="bg-background"
        />
      </template>
      <template v-else-if="caseDetailsStore.caseObj.case_version == 1">
        <v-list-subheader class="text-uppercase" v-if="!navbarHidden">
          Variant Analysis
        </v-list-subheader>

        <v-list-item
          :class="{ 'pt-3 mt-1 border-t-thin': navbarHidden }"
          prepend-icon="mdi-filter"
          append-icon="mdi-arrow-right"
          :to="{
            name: 'variants-filter',
            params: { case: caseUuid },
          }"
        >
          <template v-if="!navbarHidden"> Filter Variants </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-filter-variant"
          append-icon="mdi-arrow-right"
          :to="{
            name: 'svs-filter',
            params: { case: caseUuid },
          }"
        >
          <template v-if="!navbarHidden"> Filter SVs </template>
        </v-list-item>
      </template>
      <template v-else>
        <v-list-subheader class="text-uppercase" v-if="!navbarHidden">
          Variant Analysis (V2)
        </v-list-subheader>

        <v-list-item
          :class="{ 'pt-3 mt-1 border-t-thin': navbarHidden }"
          prepend-icon="mdi-filter"
          append-icon="mdi-arrow-right"
          :to="{
            name: 'seqvars-query',
            params: { projectUuid, caseUuid },
          }"
        >
          <template v-if="!navbarHidden"> Filter Variants </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-filter-variant"
          append-icon="mdi-arrow-right"
          :data-x-to="{
            name: 'strucvars-filter',
            params: { project: projectUuid, case: caseUuid },
          }"
        >
          <template v-if="!navbarHidden"> Filter SVs </template>
        </v-list-item>
      </template>

      <template v-if="userHasPerms('cases.update_case')">
        <v-list-subheader v-if="!navbarHidden" class="text-uppercase">
          Case Operations
        </v-list-subheader>

        <v-list-item
          :class="{ 'pt-3 mt-1 border-t-thin': navbarHidden }"
          prepend-icon="mdi-filter-settings"
          link
          @click="paneRef!.handleEditQueryPresetsClicked()"
        >
          <template v-if="!navbarHidden"> Edit Query Presets </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-comment-plus"
          link
          @click="paneRef!.handleAddCaseCommentClicked()"
        >
          <template v-if="!navbarHidden"> Add Comment </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-square-edit-outline"
          link
          @click="paneRef!.handleEditCaseStatusClicked()"
        >
          <template v-if="!navbarHidden"> Edit Status </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-playlist-edit"
          link
          @click="paneRef!.handleEditCaseNotesClicked()"
        >
          <template v-if="!navbarHidden"> Edit Notes </template>
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-file-document-edit"
          link
          @click="paneRef!.handleEditPedigreeClicked()"
        >
          <template v-if="!navbarHidden"> Edit Pedigree </template>
        </v-list-item>
        <v-list-item
          v-if="userHasPerms('cases.delete_case')"
          prepend-icon="mdi-delete-forever"
          link
          base-color="error"
          class="dropdown-item text-danger"
          @click="paneRef!.handleDestroyCaseClicked()"
        >
          <template v-if="!navbarHidden"> Delete Case </template>
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
