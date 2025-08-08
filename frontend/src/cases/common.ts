import { computed } from 'vue'

import {
  CaseVariantStatsEntry,
  useCaseDetailsStore,
} from '@/cases/stores/caseDetails'
import { useCaseListStore } from '@/cases/stores/caseList'
import { State } from '@/varfish/storeUtils'

export const overlayShow = computed(() => {
  const caseListStore = useCaseListStore()
  const caseDetailsStore = useCaseDetailsStore()
  return (
    (caseListStore?.storeState?.serverInteractions ?? 0) > 0 ||
    (caseDetailsStore?.storeState?.serverInteractions ?? 0) > 0
  )
})

export const overlayMessage = computed(() => {
  const caseListStore = useCaseListStore()
  switch (caseListStore.storeState.state) {
    case State.Initial:
      return 'initializing...'
    case State.Fetching:
      return 'communication with server...'
    case State.Active:
      return 'all data has been loaded successfully'
    case State.Error:
      return 'an error occured'
    default:
      console.error('unknown store state', caseListStore.storeState.state)
      return 'UNKNOWN STATE'
  }
})

export const tsTvRatio = (entry: CaseVariantStatsEntry): number => {
  if (!entry.ontarget_transversions) {
    return 0.0
  } else {
    return entry.ontarget_transitions / entry.ontarget_transversions
  }
}

export const downloadFile = (
  filename: string,
  contents: any,
  mimeType: string = 'application/octet-stream',
) => {
  const element = document.createElement('a')
  element.setAttribute('href', 'data:' + mimeType + ';base64,' + btoa(contents))
  element.setAttribute('download', filename)
  element.style.display = 'none'

  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
}

export const downloadPerSampleMetrics = (varStats: CaseVariantStatsEntry[]) => {
  const result = [
    ['Sample', 'Ts', 'Tv', 'Ts/Tv', 'SNVs', 'InDels', 'MNVs', 'X hom./het.'],
  ]
  for (const entry of varStats) {
    result.push(
      [
        entry.sample_name,
        entry.ontarget_transitions,
        entry.ontarget_transversions,
        tsTvRatio(entry),
        entry.ontarget_snvs,
        entry.ontarget_indels,
        entry.ontarget_mnvs,
        entry.chrx_het_hom,
      ].map((x) => x.toString()),
    )
  }
  const text = result.map((row) => row.map(String).join('\t')).join('\n')
  downloadFile('per-sample-metrics.tsv', text)
}

export interface Relatedness {
  sample0: string
  sample1: string
  ibs0: number
  ibs1: number
  rel: number
}

export const downloadRelatedness = (relData: Relatedness[]) => {
  const result = [['Sample 1', 'Sample 2', 'IBS0', 'Relatedness']]
  for (const entry of relData) {
    const { sample0, sample1, ibs0, rel } = entry
    result.push([sample0, sample1, ibs0, rel].map((x) => x.toString()))
  }
  const text = result.map((row) => row.map(String).join('\t')).join('\n')
  downloadFile('relatedness.tsv', text)
}
