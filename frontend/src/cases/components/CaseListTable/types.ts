export interface PedigreeMember {
  name: string
  father: string
  mother: string
}
export interface Case {
  sodar_uuid: string
  name: string
  status: string
  individuals: string
  num_small_vars: number
  num_svs: number
  date_created: string
  date_modified: string
  pedigree: PedigreeMember[]
}

export interface SortBy {
  key: string
  order?: boolean | 'asc' | 'desc'
}
