import { Seqvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'

import { ClientBase } from '@/varfish/apiUtils'

import { AcmgRating, AcmgRating$Api, AcmgRatingPage$Api } from './types'

type QuickPresets = any
type InheritancePresets = any
type CategoryPresets = any
type QueryShortcuts = any
type CaseQuery = any
type Case = any
type QueryResultSet = any
type QueryResultRow = any
type VariantFlags = any
type VariantComment = any

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

  async fetchProjectDefaultPresets(
    projectUuid: string,
  ): Promise<CategoryPresets> {
    return await this.fetchHelper(
      `/variants/api/query-case/project-default-presets/${projectUuid}/`,
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

  async createQuery(caseUuid: string, payload: string): Promise<CaseQuery> {
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
    queryResultSetUuid: string,
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

  async listComment(
    caseUuid: string,
    seqvar?: Seqvar,
  ): Promise<VariantComment[]> {
    let query = ''
    if (seqvar) {
      const { genomeBuild, chrom, pos, del, ins } = seqvar
      const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
      const end = pos + del.length - 1
      query =
        `?release=${release}&chromosome=${chrom}&start=${pos}` +
        `&end=${end}&reference=${del}&alternative=${ins}`
    }
    return await this.fetchHelper(
      `/variants/ajax/small-variant-comment/list-create/${caseUuid}/${query}`,
      'GET',
    )
  }

  async listProjectComment(
    projectUuid: string,
    caseUuid?: string,
    seqvar?: Seqvar,
  ): Promise<VariantComment[]> {
    let query = ''
    if (seqvar) {
      const { genomeBuild, chrom, pos, del, ins } = seqvar
      const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
      const end = pos + del.length - 1
      query =
        `?release=${release}&chromosome=${chrom}&start=${pos}` +
        `&end=${end}&reference=${del}&alternative=${ins}`
    }
    if (caseUuid) {
      query += query
        ? `&exclude_case_uuid=${caseUuid}`
        : `?exclude_case_uuid=${caseUuid}`
    }
    return await this.fetchHelper(
      `/variants/ajax/small-variant-comment/list-project/${projectUuid}/${query}`,
      'GET',
    )
  }

  async createComment(
    caseUuid: string,
    seqvar: Seqvar,
    payload: VariantComment,
  ): Promise<VariantComment> {
    const { genomeBuild, chrom, pos, del, ins } = seqvar
    const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
    const end = pos + del.length - 1
    const query =
      `release=${release}&chromosome=${chrom}&start=${pos}` +
      `&end=${end}&reference=${del}&alternative=${ins}`
    return await this.fetchHelper(
      `/variants/ajax/small-variant-comment/list-create/${caseUuid}/?${query}`,
      'POST',
      payload,
    )
  }

  async updateComment(
    commentUuid: string,
    payload: VariantComment,
  ): Promise<VariantComment> {
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

  async listFlags(caseUuid: string, seqvar?: Seqvar): Promise<VariantFlags[]> {
    let query = ''
    if (seqvar) {
      const { genomeBuild, chrom, pos, del, ins } = seqvar
      const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
      const end = pos + del.length - 1
      query =
        `?release=${release}&chromosome=${chrom}&start=${pos}` +
        `&end=${end}&reference=${del}&alternative=${ins}`
    }

    return await this.fetchHelper(
      `/variants/ajax/small-variant-flags/list-create/${caseUuid}/${query}`,
      'GET',
    )
  }

  async listProjectFlags(
    projectUuid: string,
    caseUuid?: string,
    seqvar?: Seqvar,
  ): Promise<VariantFlags[]> {
    let query = ''
    if (seqvar) {
      const { genomeBuild, chrom, pos, del, ins } = seqvar
      const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
      const end = pos + del.length - 1
      query =
        `?release=${release}&chromosome=${chrom}&start=${pos}` +
        `&end=${end}&reference=${del}&alternative=${ins}`
    }
    if (caseUuid) {
      query += query
        ? `&exclude_case_uuid=${caseUuid}`
        : `?exclude_case_uuid=${caseUuid}`
    }
    return await this.fetchHelper(
      `/variants/ajax/small-variant-flags/list-project/${projectUuid}/${query}`,
      'GET',
    )
  }

  async createFlags(caseUuid: string, seqvar: Seqvar, payload: VariantFlags) {
    const { genomeBuild, chrom, pos, del, ins } = seqvar
    const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
    const end = pos + del.length - 1
    const query =
      `release=${release}&chromosome=${chrom}&start=${pos}` +
      `&end=${end}&reference=${del}&alternative=${ins}`
    return await this.fetchHelper(
      `/variants/ajax/small-variant-flags/list-create/${caseUuid}/?${query}`,
      'POST',
      payload,
    )
  }

  async updateFlags(flagsUuid: string, payload: string) {
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

  /**
   * List all ACMG ratings for a given case possibly seqvar.
   *
   * @param caseUuid UUID of case to query.
   * @param seqvar Optional seqvar to retrieve data for, if any.
   * @returns List of
   */
  async listAcmgRating(
    caseUuid: string,
    seqvar?: Seqvar,
  ): Promise<AcmgRating[]> {
    let query = ''
    if (seqvar) {
      const { genomeBuild, chrom, pos, del, ins } = seqvar
      const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
      const end = pos + del.length - 1
      query =
        `?release=${release}&chromosome=${chrom}&start=${pos}` +
        `&end=${end}&reference=${del}&alternative=${ins}`
    }

    let nextUrl: string | null =
      `/variants/ajax/acmg-criteria-rating/list-create/${caseUuid}/${query}`
    const result: AcmgRating$Api[] = []
    while (nextUrl !== null) {
      const resultJson = (await this.fetchHelper(
        nextUrl,
        'GET',
      )) as AcmgRatingPage$Api
      result.push(...resultJson.results)
      nextUrl = resultJson.next
    }
    return result.map((item) => AcmgRating.fromJson(item))
  }

  /**
   * Create a new ACMG rating for a given case and seqvar.
   *
   * @param caseUuid UUID of case to create rating for.
   * @param seqvar Seqvar to create rating for.
   * @param payload Payload to use for creation.
   */
  async createAcmgRating(
    caseUuid: string,
    seqvar: Seqvar,
    payload: AcmgRating,
  ): Promise<AcmgRating> {
    const { genomeBuild, chrom, pos, del, ins } = seqvar
    const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
    const end = pos + del.length - 1
    const query =
      `release=${release}&chromosome=${chrom}&start=${pos}` +
      `&end=${end}&reference=${del}&alternative=${ins}`
    const result = (await this.fetchHelper(
      `/variants/ajax/acmg-criteria-rating/list-create/${caseUuid}/?${query}`,
      'POST',
      AcmgRating.toJson(payload),
    )) as AcmgRating$Api
    return AcmgRating.fromJson(result)
  }

  /**
   * Update a given ACMG rating.
   *
   * @param acmgRatingUuid UUID of the ACMG rating to update.
   * @param payload Payload to use for update.
   */
  async updateAcmgRating(
    acmgRatingUuid: string,
    payload: AcmgRating,
  ): Promise<AcmgRating> {
    const result = (await this.fetchHelper(
      `/variants/ajax/acmg-criteria-rating/update/${acmgRatingUuid}/`,
      'PATCH',
      AcmgRating.toJson(payload),
    )) as AcmgRating$Api
    return AcmgRating.fromJson(result)
  }

  /**
   * Delete a given ACMG rating.
   *
   * @param acmgRatingUuid UUID of the ACMG rating to delete.
   */
  async deleteAcmgRating(acmgRatingUuid: string): Promise<void> {
    await this.fetchHelper(
      `/variants/ajax/acmg-criteria-rating/delete/${acmgRatingUuid}/`,
      'DELETE',
    )
  }

  async generateDownloadResults(fileType: string, queryUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/query-case/download/generate/${fileType}/${queryUuid}/`,
      'GET',
    )
  }

  async statusDownloadResults(jobUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/query-case/download/status/${jobUuid}/`,
      'GET',
    )
  }

  async fetchExtraAnnoFields() {
    return await this.fetchHelper(`/variants/ajax/extra-anno-fields/`, 'GET')
  }
}
