export interface Genotype {
  ad: number
  dp: number
  gq: number
  gt: string
}

export type ExtraAnnos = any[]

export type Genotypes = {[key: string]: Genotype}

export interface ResultRowPayload {
  acmg_class_auto: string | null
  acmg_symbol: string | null
  alternative: string
  bin: number
  case_uuid: string
  chromosome_no: number
  chromosome: string
  comment_count: number | null
  details: Record<string, any>
  disease_gene: boolean
  effect: string[]
  end: number
  ensembl_gene_id: string | null
  entrez_id: string
  exac_frequency: number
  exac_homozygous: number
  exac_mis_z: number | null
  exac_pLI: number | null
  exac_syn_z: number | null
  exon_dist: number
  extra_annos: ExtraAnnos | null
  family_name: string
  flag_bookmarked: string | null
  flag_candidate: string | null
  flag_count: number | null
  flag_molecular: string | null
  flag_segregates: string | null
  flag_summary: string | null
  flag_validation: string
  flag_visual: string | null
  gene_family: string
  gene_id: string
  gene_name: string
  gene_symbol: string
  genotype: Genotypes
  gnomad_loeuf: number | null
  gnomad_mis_z: number | null
  gnomad_oe_lof: number | null
  gnomad_oe_mis: number | null
  gnomad_pLI: number | null
  gnomad_syn_z: number | null
  hgnc_id: string
  hgvs_c: string
  hgvs_p: string
  in_clinvar: boolean
  inhouse_het: number
  mgi_id: string | null
  mitomap_count: number
  mtdb_count: number
  mtdb_dloop: boolean
  mtdb_frequency: number
  pubmed_id: string
  reference: string
  refseq_hgvs_c: string | null
  refseq_transcript_id: string | null
  release: string
  rsid: string | null
  set_id: number
  start: number
  symbol: string
  transcript_id: string
  uniprot_ids: string
  variation_type: string
  var_type: string
  vcv: string
}

export interface ResultRow {
  sodar_uuid: string
  smallvariantqueryresultset: string
  release: string
  chromosome: string
  chromosome_no: number
  bin: number
  start: number
  end: number
  reference: string
  alternative: string
  payload: ResultRowPayload
}

// Below are types from 'vue3-easy-data-table' that are not exported by that package.

export type SortType = 'asc' | 'desc'

export type FilterComparison = '=' | '!=' | '>' | '>=' | '<' | '<=' | 'between'| 'in';

export type Item = Record<string, any>

export type FilterOption = {
  field: string
  comparison: 'between'
  criteria: [number, number]
} | {
  field: string
  comparison: '=' | '!='
  criteria: number | string
} | {
  field: string
  comparison: '>' | '>=' | '<' | '<='
  criteria: number
} | {
  field: number | string
  comparison: 'in'
  criteria: number[] | string[]
} | {
  field: string
  comparison: (value: any, criteria: string) => boolean
  criteria: string
}

export type Header = {
  text: string
  value: string
  sortable?: boolean
  fixed?: boolean
  width?: number
}

export type ServerOptions = {
  page: number
  rowsPerPage: number
  sortBy?: string | string[]
  sortType?: SortType | SortType[]
}

export type ClickRowArgument = Item & {
  isSelected?: boolean
  indexInCurrentPage?: number
}

export type UpdateSortArgument = {
  sortType: SortType | null
  sortBy: string
}

export type HeaderItemClassNameFunction = (header: Header, columnNumber: number) => string
export type BodyRowClassNameFunction = (item: Item, rowNumber: number) => string
export type BodyItemClassNameFunction = (column: string, rowNumber: number) => string

export type TextDirection = 'center' | 'left' | 'right'
