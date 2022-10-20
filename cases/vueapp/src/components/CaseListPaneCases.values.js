import CaseListTableCaseLink from '@cases/components/CaseListTableCaseLink.vue'
import CaseListTableShortcuts from '@cases/components/CaseListTableShortcuts.vue'
import { displayName, formatLargeInt, formatTimeAgo } from '@varfish/helpers.js'

const timeAgoFormatter = (time) => formatTimeAgo(time.value)

export const columnDefs = [
  {
    field: 'index',
    headerName: '#',
    valueGetter: 'node.rowIndex + 1',
    type: 'rightAligned',
    cellRenderer: (params) => {
      return '<span class="text-muted">#' + params.value + '</span>'
    },
    resizable: false,
    width: 70,
    suppressSizeToFit: true,
  },
  {
    field: 'name',
    headerName: 'Case Name',
    filter: 'agTextColumnFilter',
    cellRenderer: CaseListTableCaseLink,
    filterParams: {
      buttons: ['clear', 'apply'],
      closeOnApply: true,
    },
  },
  {
    field: 'status',
    headerName: 'Status',
  },
  {
    field: 'individuals',
    valueGetter: (params) => {
      return params.data.pedigree
        .map((member) => displayName(member.name))
        .join(', ')
    },
    headerName: 'Individuals',
    filter: 'agTextColumnFilter',
    filterParams: {
      buttons: ['clear', 'apply'],
      closeOnApply: true,
    },
  },
  {
    field: 'num_small_vars',
    valueFormatter: (params) => formatLargeInt(params.value),
    headerName: 'Small Vars',
    type: 'rightAligned',
    filter: 'agNumberColumnFilter',
    filterParams: {
      buttons: ['apply', 'reset'],
      closeOnApply: true,
    },
  },
  {
    field: 'num_svs',
    valueFormatter: (params) => formatLargeInt(params.value),
    headerName: 'SVs',
    type: 'rightAligned',
    filter: 'agNumberColumnFilter',
    filterParams: {
      buttons: ['apply', 'reset'],
      closeOnApply: true,
    },
  },
  {
    field: 'date_created',
    headerName: 'Creation',
    valueFormatter: timeAgoFormatter,
  },
  {
    field: 'date_modified',
    headerName: 'Last Update',
    valueFormatter: timeAgoFormatter,
  },
  {
    field: 'buttons',
    headerName: 'Shortcuts',
    cellRenderer: CaseListTableShortcuts,
    type: 'rightAligned',
  },
]
