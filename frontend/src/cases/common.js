import { computed } from 'vue'

import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
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
  mimeType = 'text/tab-separated-values',
) => {
  const blob = new Blob([contents], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const element = document.createElement('a')
  element.setAttribute('href', url)
  element.setAttribute('download', filename)
  element.style.display = 'none'

  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
  URL.revokeObjectURL(url)
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

export const downloadAlignmentStats = (bamStats) => {
  if (!bamStats) {
    return
  }

  const coverages = [0, 10, 20, 30, 40, 50]
  const result = [
    [
      'Sample',
      'Total Reads',
      'Duplicates %',
      'Insert Size Average',
      'Insert Size SD',
      'Mean Coverage',
      'Target Size',
      ...coverages.map((cov) => `Target Coverage ≥${cov}x`),
    ],
  ]

  for (const [sampleName, stats] of Object.entries(bamStats)) {
    const bamstats = stats?.bamstats
    const summary = stats?.summary
    const minCovTarget = stats?.min_cov_target || {}

    const totalReads = bamstats?.sequences ? bamstats.sequences / 2 : 0
    const duplicatesPercent = bamstats?.sequences
      ? (100.0 * bamstats['reads duplicated']) / bamstats.sequences
      : 0

    result.push([
      sampleName,
      totalReads.toString(),
      duplicatesPercent.toFixed(1),
      bamstats?.['insert size average']?.toString() ?? '-',
      bamstats?.['insert size standard deviation']?.toString() ?? '-',
      summary?.['mean coverage']?.toString() ?? '-',
      summary?.['total target size']?.toString() ?? '-',
      ...coverages.map((cov) => minCovTarget[cov]?.toString() ?? '-'),
    ])
  }

  const text = result.map((row) => row.map(String).join('\t')).join('\n')
  downloadFile('alignment-stats.tsv', text)
}
