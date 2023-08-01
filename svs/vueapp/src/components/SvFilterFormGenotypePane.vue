<script setup>
import { computed, reactive } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { integer, minValue } from '@vuelidate/validators'

import { displayName } from '@varfish/helpers'
import FilterFormGenotypePaneSex from '@variants/components/FilterFormGenotypePaneSex.vue'
import FilterFormGenotypePaneAffected from '@variants/components/FilterFormGenotypePaneAffected.vue'

/** Define component's props. */
const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  caseObj: Object,
  querySettings: Object,
})

// Return JSON string with settings from this tab to be displayed in "dev" mode.
const dumpSettings = () => {
  const result = {
    genotype: props.querySettings.genotype,
    genotype_criteria: props.querySettings.genotype_criteria,
  }
  return JSON.stringify(result)
}

/** Pre-computed mapping of member name to role in trio analysis.  Used for informative purpose only. */
const roleMap = computed(() => {
  let roles = {}
  if (props.caseObj && props.caseObj.pedigree) {
    const index = props.caseObj.index
    const pedigree = props.caseObj.pedigree
    let mother = ''
    let father = ''
    // Prepare role assignment
    for (let i = 0; i < pedigree.length; ++i) {
      if (pedigree[i].name === index) {
        father = pedigree[i].father
        mother = pedigree[i].mother
      }
    }
    // Add roles
    for (const member of pedigree) {
      const name = member.name
      if (name === index) {
        roles[name] = 'index'
      } else if (name === father) {
        roles[name] = 'father'
      } else if (name === mother) {
        roles[name] = 'mother'
      } else {
        roles[name] = 'N/A'
      }
    }
  }
  return roles
})

/** Return role from roleMap. */
const getRole = (name) => {
  if (roleMap.value) {
    return roleMap.value[name]
  }
}

/** Precomputed mapping of father for each pedigree member. */
const memberToFather = Object.fromEntries(
  props.caseObj.pedigree.map((member) => [member.name, member.father]),
)

/** Precomputed mapping of mother for each pedigree member. */
const memberToMother = Object.fromEntries(
  props.caseObj.pedigree.map((member) => [member.name, member.mother]),
)

/** Build a wrapper to go into `genotypeWrappers` below. */
const makeGenotypeWrapper = (name) =>
  computed({
    get() {
      if (props.querySettings?.genotype) {
        return props.querySettings.genotype[name]
      } else {
        return null
      }
    },
    set(newValue) {
      if (!props.querySettings) {
        return
      }

      if (newValue.endsWith('-index')) {
        // Handle new recessive index. Reset previous comp. het. settings, if any.
        for (const [key, value] of Object.entries(props.querySettings)) {
          if (
            key !== name &&
            key !== memberToFather[name] &&
            key !== memberToMother[name] &&
            ['comphet-index', 'recessive-index', 'recessive-parent'].includes(
              value,
            )
          ) {
            props.querySettings[key] = 'any'
          }
        }
        // Set index and parents
        if (newValue === 'comphet-index') {
          props.querySettings.recessive_index = name
          props.querySettings.recessive_mode = 'compound-recessive'
        } else if (newValue === 'recessive-index') {
          props.querySettings.recessive_index = name
          props.querySettings.recessive_mode = 'recessive'
        }
        for (const parent of [memberToFather[name], memberToMother[name]]) {
          if (parent) {
            props.querySettings.genotype[parent] = 'recessive-parent'
          }
        }
      } else if (props.querySettings.genotype[name].endsWith('-index')) {
        // Handle parents of previously recessive index.
        for (const parent of [memberToFather[name], memberToMother[name]]) {
          if (parent) {
            props.querySettings.genotype[parent] = 'any'
          }
        }
      } else if (props.querySettings.genotype[name] === 'recessive-parent') {
        // Prevent deselecting recessive parent.
        props.querySettings.genotype[name] = 'recessive-parent'
        return
      } else {
        props.querySettings.recessive_index = null
        props.querySettings.recessive_mode = null
      }

      props.querySettings.genotype[name] = newValue
    },
  })

const genotypeWrappers = reactive(
  Object.fromEntries(
    props.caseObj.pedigree.map((member) => [
      member.name,
      makeGenotypeWrapper(member.name),
    ]),
  ),
)

/** Initialize vuelidate. */
const v$ = useVuelidate()
defineExpose({ v$ })
</script>

<template>
  <div
    v-if="props.showFiltrationInlineHelp"
    class="alert alert-secondary small p-2 m-2"
  >
    <i-mdi-information />

    You can define genotypes and criteria matches here.
  </div>
  <table
    class="table table-striped table-hover sodar-card-table compact-form-groups"
  >
    <thead>
      <tr>
        <th class="text-muted" style="width: 10px">#</th>
        <th>Family</th>
        <th>Individual</th>
        <th>Trio Role</th>
        <th>Father</th>
        <th>Mother</th>
        <th class="text-center" style="width: 100px">Sex</th>
        <th class="text-center" style="width: 100px">Affected</th>
        <th class="text-center" style="width: 200px">Genotype</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(item, index) in props.caseObj.pedigree" :key="index">
        <td class="text-muted">{{ index + 1 }}</td>
        <td class="text-muted">{{ props.caseObj.name }}</td>
        <td>{{ displayName(item.name) }}</td>
        <td>{{ getRole(item.name) }}</td>
        <td>{{ displayName(item.name) }}</td>
        <td>{{ displayName(item.name) }}</td>
        <td class="text-center">
          <FilterFormGenotypePaneSex :sex="item.sex" />
        </td>
        <td class="text-center">
          <FilterFormGenotypePaneAffected :affected="item.affected" />
        </td>
        <td class="text-right text-muted">
          <select
            class="custom-select custom-select-sm"
            v-model="genotypeWrappers[item.name]"
          >
            <option value="any">any</option>
            <optgroup label="simple">
              <option value="ref">0/0 (wild type)</option>
              <option value="het">0/1 (het.)</option>
              <option value="hom">1/1 (hom. alt.)</option>
            </optgroup>
            <!--            <optgroup label="recessive mode">-->
            <!--              <option value="comphet-index">c/h index</option>-->
            <!--              <option value="recessive-index">recess. index</option>-->
            <!--              <option value="recessive-parent" disabled="disabled">-->
            <!--                recess. parent-->
            <!--              </option>-->
            <!--            </optgroup>-->
            <optgroup label="miscellaneous">
              <option value="variant">variant: 0/1 or 1/1</option>
              <option value="non-variant">non-variant: 0/0 or no-call</option>
            </optgroup>
          </select>
        </td>
      </tr>
    </tbody>
  </table>
  <div v-if="filtrationComplexityMode == 'dev'" class="card-footer">
    <span class="text-nowrap">
      <i-mdi-account-hard-hat />
      <strong class="pl-2">Developer Info:</strong>
    </span>
    <code>
      {{ dumpSettings() }}
    </code>
  </div>
</template>

<style scoped></style>
