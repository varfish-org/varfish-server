import { ClientBase } from '@varfish/apiUtils'

import { ExtraAnnoFields } from './types'

type QuickPresets = any
type InheritancePresets = any
type CategoryPresets = any
type QueryShortcuts = any
type CaseQuery = any
type Case = any
type QueryResultSet = any
type QueryResultRow = any
type AcmgRating = any
type VariantFlags = any

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

export interface RetrieveVariantDetailsArgs {
  case_uuid: string
  release: string
  chromosome: string
  start: number
  end: number
  reference: string
  alternative: string
  gene_id: string
}

export interface SmallVariant {
  release: string
  chromosome: string
  start: number
  end: number
  reference: string
  alternative: string
}

/**
 * Class for accessing the variants REST API.
 */
export class VariantClient extends ClientBase {
  async fetchQuickPresets(): Promise<QuickPresets> {
    return await this.fetchHelper(
      '/variants/api/query-case/quick-presets/',
      'GET',
    )
  }

  async fetchInheritancePresets(caseUuid: string): Promise<InheritancePresets> {
    return await this.fetchHelper(
      `/variants/api/query-case/inheritance-presets/${caseUuid}/`,
      'GET',
    )
  }

  async fetchCategoryPresets(categoryUuid: string): Promise<CategoryPresets> {
    return await this.fetchHelper(
      `/variants/api/query-case/category-presets/${categoryUuid}/`,
      'GET',
    )
  }

  async fetchQueryShortcuts(caseUuid: string): Promise<QueryShortcuts> {
    return await this.fetchHelper(
      `/variants/ajax/query-case/query-settings-shortcut/${caseUuid}/`,
      'GET',
    )
  }

  async fetchCaseQueries(caseUuid: string): Promise<CaseQuery[]> {
    return await this.fetchHelper(
      `/variants/ajax/query-case/list/${caseUuid}/`,
      'GET',
    )
  }

  async retrieveCase(caseUuid: string): Promise<Case> {
    return await this.fetchHelper(
      `/variants/ajax/case/retrieve/${caseUuid}/`,
      'GET',
    )
  }

  async createQuery(caseUuid, payload: string): Promise<CaseQuery> {
    return await this.fetchHelper(
      `/variants/ajax/query/list-create/${caseUuid}/`,
      'POST',
      payload,
    )
  }

  async retrieveQuery(queryUuid: string): Promise<CaseQuery> {
    return await this.fetchHelper(
      `/variants/ajax/query/retrieve-update-destroy/${queryUuid}/`,
      'GET',
    )
  }

  async listQueryResultSet(queryUuid: string): Promise<QueryResultSet[]> {
    return await this.fetchHelper(
      `/variants/ajax/query-result-set/list/${queryUuid}/`,
      'GET',
    )
  }

  async retrieveQueryResultSet(
    queryResultSetUuid: string,
  ): Promise<QueryResultSet> {
    return await this.fetchHelper(
      `/variants/ajax/query-result-set/retrieve/${queryResultSetUuid}/`,
      'GET',
    )
  }

  async listQueryResultRow(
    queryResultSetUuid,
    args?: ListArgs,
  ): Promise<QueryResultRow[]> {
    const pageNo = args?.pageNo ?? 1
    const pageSize = args?.pageSize ?? 50
    const orderByRaw = args?.orderBy ?? 'chromosome_no,start'
    const orderBy = ['start', 'end'].includes(orderByRaw)
      ? `chromosome_no,${orderByRaw}`
      : orderByRaw
    const orderDir = args?.orderDir ?? 'asc'

    const urlQuery = `?page=${pageNo}&page_size=${pageSize}&order_by=${orderBy}&order_dir=${orderDir}`
    return await this.fetchHelper(
      `/variants/ajax/query-result-row/list/${queryResultSetUuid}/${urlQuery}`,
      'GET',
    )
  }

  async retrieveQueryResultRow(
    queryResultRowUuid: string,
  ): Promise<QueryResultRow> {
    return await this.fetchHelper(
      `/variants/ajax/query-result-row/retrieve/${queryResultRowUuid}/`,
      'GET',
    )
  }

  async listCaseVariantsUserAnnotated(caseUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/variants/ajax/smallvariant/user-annotated-case/${caseUuid}/`,
      'GET',
    )
  }

  async retrieveVariantDetails(
    database: string,
    args: RetrieveVariantDetailsArgs,
  ) {
    const {
      case_uuid,
      release,
      chromosome,
      start,
      end,
      reference,
      alternative,
      gene_id,
    } = args
    const varDesc = `${release}-${chromosome}-${start}-${end}-${reference}-${alternative}`
    return await this.fetchHelper(
      `/variants/ajax/small-variant-details/${case_uuid}/${varDesc}/${database}/${gene_id}/`,
      'GET',
    )
  }

  async listComment(caseUuid, smallVariant?: SmallVariant): Promise<Comment[]> {
    let query = ''
    if (smallVariant) {
      const { release, chromosome, start, end, reference, alternative } =
        smallVariant
      query =
        `?release=${release}&chromosome=${chromosome}&start=${start}` +
        `&end=${end}&reference=${reference}&alternative=${alternative}`
    }
    return await this.fetchHelper(
      `/variants/ajax/small-variant-comment/list-create/${caseUuid}/${query}`,
      'GET',
    )
  }

  async createComment(
    caseUuid: string,
    smallVariant: SmallVariant,
    payload: Comment,
  ): Promise<Comment> {
    const { release, chromosome, start, end, reference, alternative } =
      smallVariant
    const query =
      `release=${release}&chromosome=${chromosome}&start=${start}` +
      `&end=${end}&reference=${reference}&alternative=${alternative}`
    return await this.fetchHelper(
      `/variants/ajax/small-variant-comment/list-create/${caseUuid}/?${query}`,
      'POST',
      payload,
    )
  }

  async updateComment(commentUuid, payload: string): Promise<Comment> {
    return await this.fetchHelper(
      `/variants/ajax/small-variant-comment/update/${commentUuid}/`,
      'PATCH',
      payload,
    )
  }

  async deleteComment(commentUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/small-variant-comment/delete/${commentUuid}/`,
      'DELETE',
    )
  }

  async listFlags(
    caseUuid: string,
    variant?: SmallVariant,
  ): Promise<VariantFlags[]> {
    let query = ''
    if (variant) {
      const { release, chromosome, start, end, reference, alternative } =
        variant
      query =
        `?release=${release}&chromosome=${chromosome}&start=${start}` +
        `&end=${end}&reference=${reference}&alternative=${alternative}`
    }

    return await this.fetchHelper(
      `/variants/ajax/small-variant-flags/list-create/${caseUuid}/${query}`,
      'GET',
    )
  }

  async createFlags(
    caseUuid: string,
    smallVariant: SmallVariant,
    payload: VariantFlags,
  ) {
    const { release, chromosome, start, end, reference, alternative } =
      smallVariant
    const query =
      `release=${release}&chromosome=${chromosome}&start=${start}` +
      `&end=${end}&reference=${reference}&alternative=${alternative}`
    return await this.fetchHelper(
      `/variants/ajax/small-variant-flags/list-create/${caseUuid}/?${query}`,
      'POST',
      payload,
    )
  }

  async updateFlags(flagsUuid, payload: string) {
    return await this.fetchHelper(
      `/variants/ajax/small-variant-flags/update/${flagsUuid}/`,
      'PATCH',
      payload,
    )
  }

  async deleteFlags(flagsUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/small-variant-flags/delete/${flagsUuid}/`,
      'DELETE',
    )
  }

  async listAcmgRating(caseUuid, variant?: SmallVariant = null) {
    let query = ''
    if (variant) {
      const { release, chromosome, start, end, reference, alternative } =
        variant
      query =
        `?release=${release}&chromosome=${chromosome}&start=${start}` +
        `&end=${end}&reference=${reference}&alternative=${alternative}`
    }

    return await this.fetchHelper(
      `/variants/ajax/acmg-criteria-rating/list-create/${caseUuid}/${query}`,
      'GET',
    )
  }

  async createAcmgRating(
    caseUuid: string,
    smallVariant: SmallVariant,
    payload: AcmgRating,
  ) {
    const { release, chromosome, start, end, reference, alternative } =
      smallVariant
    const query =
      `release=${release}&chromosome=${chromosome}&start=${start}` +
      `&end=${end}&reference=${reference}&alternative=${alternative}`
    return await this.fetchHelper(
      `/variants/ajax/acmg-criteria-rating/list-create/${caseUuid}/?${query}`,
      'POST',
      payload,
    )
  }

  async updateAcmgRating(acmgRatingUuid: string, payload: AcmgRating) {
    return await this.fetchHelper(
      `/variants/ajax/acmg-criteria-rating/update/${acmgRatingUuid}/`,
      'PATCH',
      payload,
    )
  }

  async deleteAcmgRating(acmgRatingUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/acmg-criteria-rating/delete/${acmgRatingUuid}/`,
      'DELETE',
    )
  }

  async generateDownloadResults(fileType, queryUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/query-case/download/generate/${fileType}/${queryUuid}`, // no trailing slash!!!
      'GET',
    )
  }

  async statusDownloadResults(jobUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/query-case/download/status/${jobUuid}/`,
      'GET',
    )
  }

  async fetchExtraAnnoFields(): Promise<ExtraAnnoFields> {
    return await this.fetchHelper(`/variants/ajax/extra-anno-fields/`, 'GET')
  }

  async fetchHpoTerms(query: string) {
    return await this.fetchHelper(
      `/variants/ajax/hpo-terms/?query=${query}`,
      'GET',
    )
  }
}
