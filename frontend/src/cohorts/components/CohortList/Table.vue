<script setup>
import debounce from 'lodash.debounce'
import { onMounted, ref, watch } from 'vue'
import EasyDataTable from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'

import ModalCohortEditor from '@/cohorts/components/ModalCohortEditor.vue'
import { useCohortsStore } from '@/cohorts/stores/cohorts'
import ModalConfirm from '@/varfish/components/ModalConfirm.vue'
import Toast from '@/varfish/components/Toast.vue'
import { formatTimeAgo } from '@/varfish/helpers'

const cohortsStore = useCohortsStore()

const modalCohortEditorRef = ref(null)

const modalConfirmRef = ref(null)

const toastRef = ref(null)

/** Update display when pagination or sorting changed. */
watch(
  [
    () => cohortsStore.tableServerOptions.page,
    () => cohortsStore.tableServerOptions.rowsPerPage,
    () => cohortsStore.tableServerOptions.sortBy,
    () => cohortsStore.tableServerOptions.sortType,
  ],
  (
    [_newPageNo, _newRowsPerPage, _newSortBy, _newSortType],
    [_oldPageNo, _oldRowsPerPage, _oldSortBy, _oldSortType],
  ) => cohortsStore.loadFromServer(),
)

/** Debounced version for reloading the table from server */
const debouncedLoadFromServer = debounce(cohortsStore.loadFromServer, 1000, {
  leading: true,
  maxWait: 2,
  trailing: true,
})

/** Update display when search term changed. */
watch(
  () => cohortsStore.searchTerm,
  (_newSearchTerm, _oldSearchTerm) => debouncedLoadFromServer(),
)

const headers = [
  { text: 'Name', value: 'name', sortable: true },
  { text: 'Creator', value: 'user.username', sortable: true },
  { text: 'Created', value: 'date_created', sortable: true },
  { text: 'Modified', value: 'date_modified', sortable: true },
  { text: '#Cases', value: 'cases.length', sortable: true },
  { text: '#Members', value: 'members_count', sortable: true },
  { text: 'Cases', value: 'cases' },
  { text: '', value: 'inaccessible_cases' },
  { text: '', value: 'buttons' },
]

/** Handle clicks on "edit cohort". */
const handleUpdateCohortClicked = async (cohortData) => {
  const cases = []
  cohortData.cases.forEach((kase) => cases.push(kase.sodar_uuid))
  try {
    const cohort = await modalCohortEditorRef.value.show({
      title: 'Update Cohort',
      modelValue: {
        name: cohortData.name,
        cases: cases,
      },
      projectsCases: cohortsStore.projectsCases,
    })

    await cohortsStore.updateCohort(cohortData.sodar_uuid, cohort)
    await cohortsStore.loadFromServer()

    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: 'The cohort was updated successfully.',
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: 'There was a problem updating the cohort.',
    })
  }
}

/** Handle clicks on "delete cohort".
 *
 * Display a modal that asks for confirmation.
 */
const handleDeleteCohortClicked = async (cohortUuid) => {
  await modalConfirmRef.value.show({
    title: 'Please Confirm Deletion',
    isDanger: true,
  })

  try {
    /** Destroy given cohort. */
    await cohortsStore.destroyCohort(cohortUuid)
    await cohortsStore.loadFromServer()

    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: 'The cohort was successfully deleted.',
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: 'There was a problem deleting the cohort.',
    })
  }
}

const getMemberCount = (cases) => {
  return cases.reduce(
    (accumulator, kase) => accumulator + kase.pedigree.length,
    0,
  )
}

const casesHaveSameRelease = (cases) => {
  return cases.every((kase) => kase.release === cases[0].release)
}

/** Load from server when mounted. */
onMounted(async () => {
  await cohortsStore.loadFromServer()
})
</script>

<template>
  <div class="row pt-3">
    <div class="col">
      <div class="card mb-3 varfish-cohort-list-card">
        <div class="card-header d-flex">
          <h4 class="col-auto">
            <i-mdi-family-tree />
            Cohort List
            <span class="badge badge-secondary">{{
              cohortsStore.cohortCount
            }}</span>
          </h4>

          <div class="col-auto ml-auto pr-0">
            <div class="input-group">
              <div class="input-group-prepend">
                <span class="input-group-text">
                  <i-mdi-account-search />
                </span>
              </div>
              <input
                v-model="cohortsStore.searchTerm"
                type="text"
                class="form-control"
                placeholder="search text"
              />
            </div>
          </div>
        </div>

        <div class="card-body p-0 position-relative">
          <EasyDataTable
            v-model:server-options="cohortsStore.tableServerOptions"
            :headers="headers"
            :items="cohortsStore.tableRows"
            table-class-name="custom-table"
            :search-value="cohortsStore.searchTerm"
            :server-items-length="cohortsStore.cohortCount"
            :loading="cohortsStore.tableLoading"
            :rows-items="[10, 20, 50, 100]"
            theme-color="#6c757d"
            alternating
            buttons-pagination
            show-index
          >
            <template #empty-message>
              <em class="ml-2 text-dark">
                <strong>No cohorts available.</strong>
              </em>
            </template>
            <template #item-date_created="{ date_created }">{{
              formatTimeAgo(date_created)
            }}</template>
            <template #item-date_modified="{ date_modified }">{{
              formatTimeAgo(date_modified)
            }}</template>
            <template #item-members_count="{ cases }">{{
              getMemberCount(cases)
            }}</template>
            <template #item-cases="{ cases }">
              <span
                v-for="kase in cases"
                :key="`case-${kase.name}`"
                class="badge-group"
              >
                <span class="badge badge-dark">{{ kase.name }}</span>
                <span class="badge badge-secondary">{{
                  kase.pedigree.length
                }}</span>
                <span
                  class="badge badge-light release"
                  style="border: 1px solid #6c757d !important; border-left: 0"
                  >{{ kase.release }}</span
                >
              </span>
            </template>
            <template #item-inaccessible_cases="{ inaccessible_cases }">
              <span class="badge-group">
                <span v-if="inaccessible_cases > 0" class="badge badge-warning">
                  <i-mdi-alert-decagram />
                  Inaccessible Cases
                </span>
                <span v-if="inaccessible_cases > 0" class="badge badge-dark">
                  {{ inaccessible_cases }}
                </span>
              </span>
            </template>
            <template #item-buttons="item">
              <div class="btn-group btn-group-sm">
                <a
                  class="btn btn-sm btn-primary"
                  :class="!casesHaveSameRelease(item.cases) ? 'disabled' : ''"
                  style="font-size: 80%"
                  :href="`/variants/${cohortsStore.project.sodar_uuid}/project-cases/filter/cohort/${item.sodar_uuid}/`"
                >
                  <i-mdi-filter />
                </a>
                <button
                  :disabled="item.inaccessible_cases > 0"
                  type="button"
                  class="btn btn-sm btn-primary"
                  style="font-size: 80%"
                  @click="handleUpdateCohortClicked(item)"
                >
                  <i-mdi-edit />
                </button>
                <button
                  :disabled="item.inaccessible_cases > 0"
                  type="button"
                  class="btn btn-sm btn-danger"
                  style="font-size: 80%"
                  @click="handleDeleteCohortClicked(item.sodar_uuid)"
                >
                  <i-mdi-delete />
                </button>
              </div>
            </template>
          </EasyDataTable>
        </div>
      </div>
    </div>
    <ModalCohortEditor ref="modalCohortEditorRef" />
    <ModalConfirm ref="modalConfirmRef" />
    <Toast ref="toastRef" :autohide="false" />
  </div>
</template>

<style scoped>
.custom-table {
  --easy-table-border: 0px solid #000000;
  --easy-table-row-border: 0px solid #000000;
  /*--easy-table-body-row-font-size: 14px;*/
  /*--easy-table-header-font-size: 14px;*/
  /*--easy-table-footer-font-size: 12px;*/
}
</style>
