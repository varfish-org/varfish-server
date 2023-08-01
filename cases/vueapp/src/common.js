import { StoreState, useCasesStore } from '@cases/stores/cases'
import { updateUserSetting } from '@varfish/user-settings'
import { computed, nextTick, onMounted, watch } from 'vue'

export const overlayShow = computed(() => {
  const casesStore = useCasesStore()
  return (
    !casesStore.storeState ||
    casesStore.storeState.value === StoreState.initializing ||
    casesStore.serverInteractions.value
  )
})

export const overlayMessage = computed(() => {
  const casesStore = useCasesStore()
  if (
    !casesStore.storeState ||
    casesStore.storeState.value === StoreState.initializing
  ) {
    return 'initializing...'
  } else {
    return 'communication with server...'
  }
})

export const connectTopRowControls = () => {
  const casesStore = useCasesStore()

  // Reflect "show inline help" and "filter complexity" setting in navbar checkbox.
  watch(
    () => casesStore.showInlineHelp,
    (newValue, oldValue) => {
      if (newValue !== oldValue && casesStore.appContext) {
        updateUserSetting(
          casesStore.appContext.csrf_token,
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
    () => casesStore.complexityMode,
    (newValue, oldValue) => {
      if (newValue !== oldValue && casesStore.appContext) {
        updateUserSetting(
          casesStore.appContext.csrf_token,
          'vueapp.filtration_complexity_mode',
          newValue,
        )
      }
      const elem = $('#vueapp-filtration-complexity-mode')
      if (elem && elem.val(newValue)) {
        elem.val(newValue).change()
      }
    },
  )

  // Vice versa.
  onMounted(() => {
    const handleUpdate = () => {
      const casesStore = useCasesStore()
      casesStore.showInlineHelp = $('#vueapp-filtration-inline-help').prop(
        'checked',
      )
      casesStore.complexityMode = $('#vueapp-filtration-complexity-mode').val()
    }
    nextTick(() => {
      handleUpdate()
      $('#vueapp-filtration-inline-help').change(handleUpdate)
      $('#vueapp-filtration-complexity-mode').change(handleUpdate)
    })
  })
}

export const tsTvRatio = (entry) => {
  if (!entry.ontarget_transversions) {
    return 0.0
  } else {
    return entry.ontarget_transitions / entry.ontarget_transversions
  }
}

export const downloadFile = (
  filename,
  contents,
  mimeType = 'application/octet-stream',
) => {
  const element = document.createElement('a')
  element.setAttribute('href', 'data:' + mimeType + ';base64,' + btoa(contents))
  element.setAttribute('download', filename)
  element.style.display = 'none'

  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
}

export const downloadPerSampleMetrics = (varStats) => {
  const result = [
    ['Sample', 'Ts', 'Tv', 'Ts/Tv', 'SNVs', 'InDels', 'MNVs', 'X hom./het.'],
  ]
  for (const entry of varStats) {
    result.push([
      entry.sample_name,
      entry.ontarget_transitions,
      entry.ontarget_transversions,
      tsTvRatio(entry),
      entry.ontarget_snvs,
      entry.ontarget_indels,
      entry.ontarget_mnvs,
      entry.chrx_het_hom,
    ])
  }
  const text = result.map((row) => row.map(String).join('\t')).join('\n')
  downloadFile('per-sample-metrics.tsv', text)
}

export const downloadRelatedness = (relData) => {
  const result = [['Sample 1', 'Sample 2', 'IBS0', 'Relatedness']]
  for (const entry of relData) {
    const { sample0, sample1, ibs0, rel } = entry
    result.push([sample0, sample1, ibs0, rel])
  }
  const text = result.map((row) => row.map(String).join('\t')).join('\n')
  downloadFile('relatedness.tsv', text)
}
