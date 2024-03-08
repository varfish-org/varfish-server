<script setup lang="ts">
import { watch, onMounted, nextTick } from 'vue'

import { overlayShow, overlayMessage } from '@cases/common'
import { useCaseListStore } from '@cases/stores/caseList'
import CaseListHeader from '@cases/components/CaseList/Header.vue'
import CaseListContent from '@cases/components/CaseList/Content.vue'
import Overlay from '@varfish/components/Overlay.vue'
import { updateUserSetting } from '@varfish/userSettings'

const props = defineProps<{
  currentTab: string
  presetSet?: string
}>()

const appContext = JSON.parse(
  document
    .getElementById('sodar-ss-app-context')
    ?.getAttribute('app-context') ?? '{}',
)

const caseListStore = useCaseListStore()
caseListStore.initialize(appContext.csrf_token, appContext.project.sodar_uuid)

// Reflect "show inline help" and "filter complexity" setting in navbar checkbox.
watch(
  () => caseListStore.showInlineHelp,
  (newValue, oldValue) => {
    if (newValue !== oldValue && caseListStore.csrfToken) {
      updateUserSetting(
        caseListStore.csrfToken,
        'vueapp.filtration_inline_help',
        newValue,
      )
    }
    const elem = $('#vueapp-filtration-inline-help')
    if (elem) {
      elem.prop('checked', newValue)
    }
  },
)
watch(
  () => caseListStore.complexityMode,
  (newValue, oldValue) => {
    if (newValue !== oldValue && caseListStore.csrfToken) {
      updateUserSetting(
        caseListStore.csrfToken,
        'vueapp.filtration_complexity_mode',
        newValue,
      )
    }
    const elem = $('#vueapp-filtration-complexity-mode')
    if (elem && elem.val(newValue)) {
      elem.val(newValue).trigger('change')
    }
  },
)

// Vice versa.
onMounted(() => {
  const handleUpdate = () => {
    const caseListStore = useCaseListStore()
    caseListStore.showInlineHelp = $('#vueapp-filtration-inline-help').prop(
      'checked',
    )
    caseListStore.complexityMode = String(
      $('#vueapp-filtration-complexity-mode').val(),
    )
  }
  nextTick(() => {
    handleUpdate()
    $('#vueapp-filtration-inline-help').on('change', handleUpdate)
    $('#vueapp-filtration-complexity-mode').on('change', handleUpdate)
  })
})
</script>

<template>
  <div class="d-flex flex-column h-100">
    <CaseListHeader />

    <div
      class="varfish-overlay-wrap position-relative flex-grow-1 d-flex flex-column"
    >
      <CaseListContent
        :current-tab="props.currentTab"
        :preset-set="props.presetSet"
      />
      <Overlay v-if="overlayShow" :message="overlayMessage" />
    </div>
  </div>
</template>
