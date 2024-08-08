<script setup lang="ts">
import { useCaseListStore } from '@/cases/stores/caseList'
import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import TheNavBar from '@/cases/components/TheNavBar/TheNavBar.vue'
import { ref } from 'vue'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** The case UUID. */
  caseUuid?: string
}>()

const caseListStore = useCaseListStore()

/** Whether to hide the navigation bar; component state. */
const navbarHidden = ref<boolean>(false)
/** Whether to hide the variant details pane; component state. */
const detailsHidden = ref<boolean>(true)
// Messages to display in VSnackbarQueue; component state. */
const messages = ref<SnackbarMessage[]>([])

const userHasPerms = (perm: string) =>
  caseListStore.userPerms && caseListStore.userPerms.includes(perm)
</script>

<template>
  <v-app id="seqvars-query">
    <TheAppBar
      :show-left-panel-button="true"
      :show-right-panel-button="true"
      v-model:hide-left-panel="navbarHidden"
      v-model:hide-right-panel="detailsHidden"
    />
    <TheNavBar :navbar-hidden="navbarHidden">
      <v-list-item
        prepend-icon="mdi-arrow-left"
        :to="{
          name: 'case-detail-overview',
          params: { project: projectUuid, case: caseUuid },
        }"
      >
        <template v-if="!navbarHidden"> Back to Case </template>
      </v-list-item>

      <v-list-subheader class="text-uppercase" v-if="!navbarHidden">
        Variant Analysis (V2)
      </v-list-subheader>
      <v-list-item
        prepend-icon="mdi-filter-variant"
        :data-x-to="{
          name: 'strucvars-query',
          params: { case: caseUuid },
        }"
      >
        <template v-if="!navbarHidden"> Go To SV Filtration </template>
      </v-list-item>

      <v-list-subheader class="text-uppercase" v-if="!navbarHidden">
        Variant Analysis (V2)
      </v-list-subheader>
    </TheNavBar>
    <div class="pa-3">
      <v-main>
        <!-- <CaseDetailPane
          ref="paneRef"
          :project-uuid="props.projectUuid"
          :case-uuid="props.caseUuid"
          :current-tab="props.currentTab"
        /> -->
      </v-main>
    </div>
    <v-snackbar-queue
      v-model="messages"
      timer="5000"
      close-on-content-click
    ></v-snackbar-queue>
  </v-app>
</template>
