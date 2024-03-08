export type QuickPresets = any
export type InheritancePresets = any
export type CategoryPresets = any
export type QuerySettingsShortcuts = any
export type CaseSvQuery = any
export type SvQueryResultSet = any
export type SvQueryResultRow = any
export type SvComment = any
export type SvFlags = any

/**
 * Encode the list arguments.
 */
export interface ListArgs {
  pageNo: number
  pageSize: number
  orderBy?: string
  orderDir?: string
  queryString?: string
}

export interface StructuralVariant {
  release: string
  chromosome: string
  start: number
  end: number
  reference: string
  alternative: string
  sv_type: string
  sv_sub_type: string
}
