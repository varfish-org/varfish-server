<script setup>
import FilterFormGenotypePaneAffected from '@variants/components/FilterForm/GenotypePaneAffected.vue'
import FilterFormGenotypePaneSex from '@variants/components/FilterForm/GenotypePaneSex.vue'
import { displayName } from '@varfish/helpers'
import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import { useCaseListStore } from '@cases/stores/caseList'

/** Define emits. */
const emit = defineEmits(['editPedigreeClick'])

const caseListStore = useCaseListStore()

const userHasPerms = (perm) =>
  caseListStore.userPerms && caseListStore.userPerms.includes(perm)

const caseDetailsStore = useCaseDetailsStore()
</script>

<template>
  <div class="card mb-3 varfish-case-list-card flex-grow-1">
    <div class="row card-header p-2 pl-2">
      <h5 class="col-auto ml-0 mr-0 mb-0">
        <i-mdi-family-tree />
        Pedigree
      </h5>
      <div v-if="userHasPerms('cases.update_case')" class="btn-group ml-auto">
        <a
          class="btn btn-sm btn-primary"
          href="#"
          @click.prevent="emit('editPedigreeClick')"
        >
          <i-mdi-file-document-edit />
          Edit Pedigree
        </a>
      </div>
    </div>
    <table class="table table-striped table-hover">
      <thead>
        <tr>
          <th style="width: 30%">Name</th>
          <th style="width: 30%">Father</th>
          <th style="width: 30%">Mother</th>
          <th style="width: 0">Sex</th>
          <th style="width: 0">Affected</th>
          <th style="width: 0">Variants?</th>
        </tr>
      </thead>
      <tbody>
        <template v-if="caseDetailsStore.caseObj">
          <tr v-for="member in caseDetailsStore.caseObj.pedigree">
            <td>
              {{ displayName(member.name) }}
            </td>
            <td>
              {{ displayName(member.father) }}
            </td>
            <td>
              {{ displayName(member.mother) }}
            </td>
            <td class="text-center">
              <FilterFormGenotypePaneSex :sex="member.sex" />
            </td>
            <td class="text-center">
              <FilterFormGenotypePaneAffected :affected="member.affected" />
            </td>
            <td class="text-center">
              <i-fa-solid-check v-if="member.has_gt_entries" />
              <i-fa-solid-times v-if="!member.has_gt_entries" />
            </td>
          </tr>
        </template>
        <tr v-else>
          <td colspan="6" class="text-muted text-center font-italic">
            No individuals in case.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
