import { StoreState, useCohortsStore } from '@cohorts/stores/cohorts'
import { updateUserSetting } from '@varfish/user-settings'
import { computed, nextTick, onMounted, watch } from 'vue'

export const overlayShow = computed(() => {
  const cohortsStore = useCohortsStore()
  return (
    !cohortsStore.storeState ||
    cohortsStore.storeState.value === StoreState.initializing ||
    cohortsStore.serverInteractions
  )
})

export const overlayMessage = computed(() => {
  const cohortsStore = useCohortsStore()
  if (
    !cohortsStore.storeState ||
    cohortsStore.storeState.value === StoreState.initializing
  ) {
    return 'initializing...'
  } else {
    return 'communication with server...'
  }
})

export const connectTopRowControls = () => {
  const cohortsStore = useCohortsStore()

  // Reflect "show inline help" and "filter complexity" setting in navbar checkbox.
  watch(
    () => cohortsStore.showInlineHelp,
    (newValue, oldValue) => {
      if (newValue !== oldValue && cohortsStore.appContext) {
        updateUserSetting(
          cohortsStore.appContext.csrf_token,
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
    () => cohortsStore.complexityMode,
    (newValue, oldValue) => {
      if (newValue !== oldValue && cohortsStore.appContext) {
        updateUserSetting(
          cohortsStore.appContext.csrf_token,
          'vueapp.filtration_complexity_mode',
          newValue,
        )
      }
      const elem = $('#vueapp-filtration-complexity-mode')
      if (elem) {
        elem.val(newValue).change()
      }
    },
  )

  // Vice versa.
  onMounted(() => {
    const handleUpdate = () => {
      const cohortsStore = useCohortsStore()
      cohortsStore.showInlineHelp = $('#vueapp-filtration-inline-help').prop(
        'checked',
      )
      cohortsStore.complexityMode = $(
        '#vueapp-filtration-complexity-mode',
      ).val()
    }
    nextTick(() => {
      handleUpdate()
      $('#vueapp-filtration-inline-help').change(handleUpdate)
      $('#vueapp-filtration-complexity-mode').change(handleUpdate)
    })
  })
}
