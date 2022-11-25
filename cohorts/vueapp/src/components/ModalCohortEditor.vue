<script setup>
/**
 * A component for showing a modal to create and edit cohorts.
 *
 * You can configure it either by setting the props or handing the props to the show() method.
 *
 * You can react on the "confirm button clicked" event either by handling the "confirm" event
 * or use the Promise returned by show with its resolve function.  Both the event and the resolve
 * function will be passed the input and the "props.extraData" value.
 */

import { onMounted, reactive, ref, computed } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { required } from '@vuelidate/validators'

import ModalBase from '@varfish/components/ModalBase.vue'
import { randomString } from '@varfish/common.js'
import { copy } from '@varfish/helpers.js'

const props = defineProps({
  title: {
    type: String,
    default: 'Please Enter',
  },
  noHeader: {
    type: Boolean,
    default: false,
  },
  idSuffix: {
    type: String,
    default: randomString(),
  },
  modelValue: {
    type: Object,
    default: {
      name: '',
      cases: [],
    },
  },
  modalClass: {
    type: String,
    default: 'modal-xl',
  },
  projectsCases: {
    type: Array,
    default: [],
  },
})

/** Define the emits. */
const emit = defineEmits(['cancel', 'confirm', 'update:modelValue'])

/** Copy of props to allow overriding with arguments of show(). */
const propsCopy = ref(copy(props))

/** Ref to the inner modal. */
const innerModalRef = ref(null)

/** Whether the promise was resolved already. */
const promiseCompleted = ref(false)

/** Ref to the resolve function promise returned by show(). */
const resolveRef = ref(null)

const projectsCasesSelected = ref({})

// NB: it probably makes no sense to reject on cancel, but we emit the 'cancel' event nevertheless.
// /** Ref to the reject function promise returned by show(). */
// const rejectRef = ref(null)

/** Reset the inner state. */
const reset = () => {
  promiseCompleted.value = false
  resolveRef.value = null
  // rejectRef.value = null
}

/** Show the modal. */
const show = (args) => {
  propsCopy.value = reactive({
    ...props,
    ...copy(args),
  })
  buildProjectCasesSelected()

  reset()
  innerModalRef.value.show()
  return new Promise(function (resolve /*, reject*/) {
    resolveRef.value = resolve
    // rejectRef.value = reject
  })
}

/** Hide the modal. */
const hide = () => {
  innerModalRef.value.hide()
}

/** Event handler for confirm button. */
const onConfirm = () => {
  if (!promiseCompleted.value) {
    // don't handle twice
    promiseCompleted.value = true
    resolveRef.value(propsCopy.value.modelValue)
    emit('confirm', propsCopy.value.modelValue)
    hide()
  }
}

/** Event handler for cancel button. */
const onCancel = () => {
  if (!promiseCompleted.value) {
    // don't handle twice
    // rejectRef.value(propsCopy.value.extraData)
    emit('cancel', propsCopy.value.extraData)
    hide()
  }
}

import { helpers } from '@vuelidate/validators'

const selectAtLeastTwoCases = helpers.withMessage(
  'Select at least two cases',
  (value) => value.length > 1
)

const selectAtLeastOneCase = helpers.withMessage(
  'Select at least one case',
  (value) => value.length > 0
)

/** The state to use in vuelidate. */
const formState = {
  name: computed(() => propsCopy.value.modelValue['name']),
  cases: computed(() => propsCopy.value.modelValue['cases']),
}

const rules = {
  name: { required },
  cases: { selectAtLeastOneCase, selectAtLeastTwoCases },
}

// /** Create vuelidate object. */
const v$ = useVuelidate(rules, formState)

/** Initialize form value and vuelidate. */
onMounted(() => {
  v$.value.$touch()
})

const getSelectedProjectCasesCount = (projectCases) => {
  let count = 0
  const selectedCases = new Set(propsCopy.value.modelValue.cases)
  projectCases.forEach((kase) => {
    if (selectedCases.has(kase.sodar_uuid)) {
      count++
    }
  })
  return count
}

const getSelectedCasesCount = computed(() => {
  return propsCopy.value.modelValue.cases.length
})

const getSelectedProjectMembersCount = (projectCases) => {
  let count = 0
  const selectedCases = new Set(propsCopy.value.modelValue.cases)
  projectCases.forEach((kase) => {
    if (selectedCases.has(kase.sodar_uuid)) {
      count += kase.pedigree.length
    }
  })
  return count
}

const getSelectedMembersCount = computed(() => {
  let count = 0
  propsCopy.value.projectsCases.forEach((project) => {
    const selectedCases = new Set(propsCopy.value.modelValue.cases)
    project.case_set.forEach((kase) => {
      if (selectedCases.has(kase.sodar_uuid)) {
        count += kase.pedigree.length
      }
    })
  })
  return count
})

const buildProjectCasesSelected = () => {
  propsCopy.value.projectsCases.forEach((project) => {
    projectsCasesSelected.value[project.sodar_uuid] = {
      indeterminate: computed(() => {
        const currentSelection = new Set(propsCopy.value.modelValue.cases)
        const allSet = project.case_set.every((kase) =>
          currentSelection.has(kase.sodar_uuid)
        )
        if (allSet) return false
        const noneSet = project.case_set.every(
          (kase) => !currentSelection.has(kase.sodar_uuid)
        )
        return !noneSet
      }),
      checked: computed({
        get() {
          const currentSelection = new Set(propsCopy.value.modelValue.cases)
          return project.case_set.every((kase) =>
            currentSelection.has(kase.sodar_uuid)
          )
        },
        set(newValue) {
          if (newValue) {
            const currentSelection = new Set(propsCopy.value.modelValue.cases)
            project.case_set.forEach((kase) => {
              currentSelection.add(kase.sodar_uuid)
            })
            propsCopy.value.modelValue.cases = Array.from(currentSelection)
          } else {
            const currentSelection = new Set(propsCopy.value.modelValue.cases)
            project.case_set.forEach((kase) => {
              currentSelection.delete(kase.sodar_uuid)
            })
            propsCopy.value.modelValue.cases = Array.from(currentSelection)
          }
        },
      }),
    }
  })
}

const computeProgressBar = (selected, total) => {
  if (total === 0) {
    return 0
  }
  return (100 * selected) / total
}

defineExpose({ show, hide })
</script>

<template>
  <ModalBase
    ref="innerModalRef"
    :title="propsCopy.title"
    :no-header="propsCopy.noHeader"
    :modal-class="propsCopy.modalClass"
    @close="onCancel"
  >
    <template #default>
      <div class="row">
        <div class="col">
          <div class="input-group input-group-sm">
            <div class="input-group-prepend">
              <span class="input-group-text">
                Name
                <span v-if="v$.name.$errors.length > 0" class="text-danger"
                  ><strong>*</strong></span
                >
              </span>
            </div>
            <input
              type="text"
              class="form-control"
              v-model="propsCopy.modelValue.name"
            />
          </div>
        </div>
        <div class="col-2">
          <div class="input-group input-group-sm">
            <div class="input-group-prepend">
              <span class="input-group-text">
                Selected Cases
                <template v-if="v$.cases.$errors.length > 0">
                  <span
                    :class="
                      v$.cases.$errors.length > 0 ? 'text-danger' : 'text-muted'
                    "
                    ><strong>*</strong></span
                  >
                  <span
                    :class="
                      v$.cases.$errors.length > 1 ? 'text-danger' : 'text-muted'
                    "
                    ><strong>*</strong></span
                  >
                </template>
              </span>
            </div>
            <div class="input-group-append">
              <span class="input-group-text">
                <strong>{{ getSelectedCasesCount }}</strong>
              </span>
            </div>
          </div>
        </div>
        <div class="col-3">
          <div class="input-group input-group-sm">
            <div class="input-group-prepend">
              <span class="input-group-text"> Selected Members </span>
            </div>
            <div class="input-group-append">
              <span class="input-group-text">
                <strong>{{ getSelectedMembersCount }}</strong>
              </span>
            </div>
          </div>
        </div>
      </div>
      <div class="row mt-3" v-for="project in propsCopy.projectsCases">
        <div class="col">
          <div id="accordion" class="accordion">
            <div class="card mb-0">
              <div
                class="card-header form-inline"
                :id="'heading-project-' + project.sodar_uuid"
              >
                <div class="input-group input-group-sm">
                  <div class="input-group-prepend">
                    <div class="input-group-text">
                      <input
                        type="checkbox"
                        v-model="
                          projectsCasesSelected[project.sodar_uuid].checked
                        "
                        :indeterminate="
                          projectsCasesSelected[project.sodar_uuid]
                            .indeterminate
                        "
                      />
                    </div>
                  </div>
                  <button
                    class="btn btn-primary btn-sm collapsed"
                    type="button"
                    data-toggle="collapse"
                    :data-target="'#collapse-project-' + project.sodar_uuid"
                    aria-expanded="false"
                    :aria-controls="'collapse-project-' + project.sodar_uuid"
                  >
                    <strong>{{ project.title }}</strong>
                    <span class="ml-1 badge badge-light">{{
                      project.case_set.length
                    }}</span>
                  </button>
                </div>
                <div class="input-group input-group-sm ml-3">
                  <div class="input-group-prepend">
                    <span class="input-group-text"> Selected Cases </span>
                  </div>
                  <div class="input-group-append">
                    <span class="input-group-text">
                      <strong>{{
                        getSelectedProjectCasesCount(project.case_set)
                      }}</strong>
                    </span>
                  </div>
                </div>
                <div class="input-group input-group-sm ml-3">
                  <div class="input-group-prepend">
                    <span class="input-group-text"> Selected Members </span>
                  </div>
                  <div class="input-group-append">
                    <span class="input-group-text">
                      <strong>{{
                        getSelectedProjectMembersCount(project.case_set)
                      }}</strong>
                    </span>
                  </div>
                </div>
              </div>
              <div class="progress" style="height: 3px">
                <div
                  class="progress-bar"
                  role="progressbar"
                  :style="`width: ${computeProgressBar(
                    getSelectedProjectCasesCount(project.case_set),
                    project.case_set.length
                  )}%`"
                  :aria-valuenow="
                    computeProgressBar(
                      getSelectedProjectCasesCount(project.case_set),
                      project.case_set.length
                    )
                  "
                  aria-valuemin="0"
                  aria-valuemax="100"
                ></div>
              </div>
              <div
                :id="'collapse-project-' + project.sodar_uuid"
                class="collapse"
                :aria-labelledby="'heading-project-' + project.sodar_uuid"
                data-parent="#accordion"
              >
                <div class="card-body pb-2">
                  <div
                    class="form-check form-check-inline"
                    v-for="kase in project.case_set"
                  >
                    <input
                      type="checkbox"
                      class="form-check-input"
                      v-model="propsCopy.modelValue.cases"
                      :id="'case-' + kase.sodar_uuid"
                      :value="kase.sodar_uuid"
                    />
                    <label
                      class="form-check-label badge-group"
                      :for="'case-' + kase.sodar_uuid"
                    >
                      <span class="badge badge-dark">{{ kase.name }}</span>
                      <span class="badge badge-secondary">{{
                        kase.pedigree.length
                      }}</span>
                      <span
                        class="badge badge-light release"
                        style="
                          border: 1px solid #6c757d !important;
                          border-left: 0;
                        "
                        >{{ kase.release }}</span
                      >
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="ml-auto">
        <a
          class="btn btn-success mr-2"
          :class="{ disabled: v$.$error }"
          href="#"
          @click.prevent="onConfirm"
        >
          <i-mdi-check />
          Confirm
        </a>
        <a class="btn btn-secondary" @click.prevent="onCancel">
          <i-mdi-close />
          Cancel
        </a>
      </div>
    </template>
  </ModalBase>
</template>
