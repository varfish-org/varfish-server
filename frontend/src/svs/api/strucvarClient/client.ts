import { Strucvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'

import { ClientBase } from '@/varfish/apiUtils'

import {
  AcmgRating,
  AcmgRating$Api,
  AcmgRatingPage$Api,
  CaseSvQuery,
  CategoryPresets,
  InheritancePresets,
  ListArgs,
  QuerySettingsShortcuts,
  QuickPresets,
  SvAcmgRating,
  SvComment,
  SvFlags,
  SvQueryResultRow,
  SvQueryResultSet,
} from './types'

/**
 * Class for accessing the SV REST API.
 */
export class SvClient extends ClientBase {
  async fetchQuickPresets(): Promise<QuickPresets> {
    return await this.fetchHelper('/svs/ajax/query-case/quick-presets/', 'GET')
  }

  async fetchInheritancePresets(caseUuid: string): Promise<InheritancePresets> {
    return await this.fetchHelper(
      `/svs/ajax/query-case/inheritance-presets/${caseUuid}/`,
      'GET',
    )
  }

  async fetchCategoryPresets(category: string): Promise<CategoryPresets> {
    return await this.fetchHelper(
      `/svs/ajax/query-case/category-presets/${category}/`,
      'GET',
    )
  }

  async retrieveQuerySettingsShortcut(
    caseUuid: string,
  ): Promise<QuerySettingsShortcuts> {
    return await this.fetchHelper(
      `/svs/ajax/query-case/query-settings-shortcut/${caseUuid}/`,
      'GET',
    )
  }

  async listSvQuery(caseUuid: string): Promise<CaseSvQuery> {
    return await this.fetchHelper(
      `/svs/ajax/sv-query/list-create/${caseUuid}/`,
      'GET',
    )
  }

  async createSvQuery(caseUuid: string, payload: string): Promise<CaseSvQuery> {
    return await this.fetchHelper(
      `/svs/ajax/sv-query/list-create/${caseUuid}/`,
      'POST',
      payload,
    )
  }

  async retrieveSvQuery(svQueryUuid: string): Promise<CaseSvQuery> {
    return await this.fetchHelper(
      `/svs/ajax/sv-query/retrieve-update-destroy/${svQueryUuid}/`,
      'GET',
    )
  }

  async listSvQueryResultSet(svQueryUuid: string): Promise<SvQueryResultSet[]> {
    return await this.fetchHelper(
      `/svs/sv-query-result-set/list/${svQueryUuid}/`,
      'GET',
    )
  }

  async retrieveSvQueryResultSet(
    svQueryResultUuid: string,
  ): Promise<SvQueryResultSet> {
    return await this.fetchHelper(
      `/svs/sv-query-result-set/retrieve/${svQueryResultUuid}/`,
      'GET',
    )
  }

  async listSvQueryResultRow(svQueryResultSetUuid: string, args?: ListArgs) {
    const pageNo = args?.pageNo ?? 1
    const pageSize = args?.pageSize ?? 50
    const orderByRaw = args?.orderBy ?? 'chromosome_no,start'
    const orderBy = ['start', 'end'].includes(orderByRaw)
      ? `chromosome_no,${orderByRaw}`
      : orderByRaw
    const orderDir = args?.orderDir ?? 'asc'

    const urlQuery = `?page=${pageNo}&page_size=${pageSize}&order_by=${orderBy}&order_dir=${orderDir}`
    return await this.fetchHelper(
      `/svs/sv-query-result-row/list/${svQueryResultSetUuid}/${urlQuery}`,
      'GET',
    )
  }

  async retrieveSvQueryResultRow(
    queryResultRowUuid: string,
  ): Promise<SvQueryResultRow> {
    return await this.fetchHelper(
      `/svs/sv-query-result-row/retrieve/${queryResultRowUuid}/`,
      'GET',
    )
  }

  /** List comments for the given case, optionally for the given `sv`. */
  async listComment(caseUuid: string, strucvar?: Strucvar) {
    let query = ''
    if (strucvar) {
      const { svType, genomeBuild, chrom, start } = strucvar
      const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
      let stop
      if (svType === 'INS' || svType === 'BND') {
        stop = strucvar.start
      } else {
        stop = strucvar.stop
      }
      query =
        `?release=${release}&chromosome=${chrom}&start=${start}` +
        `&end=${stop}&sv_type=${svType}&sv_sub_type=${svType}`
    }

    return await this.fetchHelper(
      `/svs/ajax/structural-variant-comment/list-create/${caseUuid}/${query}`,
      'GET',
    )
  }

  async createComment(
    caseUuid: string,
    strucvar: Strucvar,
    payload: SvComment,
  ): Promise<SvComment> {
    const { svType, genomeBuild, chrom, start } = strucvar
    const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
    let stop
    if (svType === 'INS' || svType === 'BND') {
      stop = strucvar.start
    } else {
      stop = strucvar.stop
    }
    const query =
      `release=${release}&chromosome=${chrom}&start=${start}` +
      `&end=${stop}&sv_type=${svType}&sv_sub_type=${svType}`

    return await this.fetchHelper(
      `/svs/ajax/structural-variant-comment/list-create/${caseUuid}/?${query}`,
      'POST',
      payload,
    )
  }

  async updateComment(
    commentUuid: string,
    payload: SvComment,
  ): Promise<SvComment> {
    return await this.fetchHelper(
      `/svs/ajax/structural-variant-comment/retrieve-update-destroy/${commentUuid}/`,
      'PATCH',
      payload,
    )
  }

  async deleteComment(commentUuid: string) {
    return await this.fetchHelper(
      `/svs/ajax/structural-variant-comment/retrieve-update-destroy/${commentUuid}/`,
      'DELETE',
    )
  }

  async listProjectComment(
    projectUuid: string,
    caseUuid?: string,
    strucvar?: Strucvar,
  ): Promise<SvComment[]> {
    let query = ''
    if (strucvar) {
      const { svType, genomeBuild, chrom, start } = strucvar
      const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
      let stop
      if (svType === 'INS' || svType === 'BND') {
        stop = strucvar.start
      } else {
        stop = strucvar.stop
      }
      query =
        `?release=${release}&chromosome=${chrom}&start=${start}` +
        `&end=${stop}&sv_type=${svType}&sv_sub_type=${svType}`
    }
    if (caseUuid) {
      query += query
        ? `&exclude_case_uuid=${caseUuid}`
        : `?exclude_case_uuid=${caseUuid}`
    }
    return await this.fetchHelper(
      `/svs/ajax/structural-variant-comment/list-project/${projectUuid}/${query}`,
      'GET',
    )
  }

  /** List flags for the given case, optionally for the given `sv`. */
  async listFlags(caseUuid: string, strucvar?: Strucvar): Promise<SvFlags[]> {
    let query = ''
    if (strucvar) {
      const { svType, genomeBuild, chrom, start } = strucvar
      const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
      let stop
      if (svType === 'INS' || svType === 'BND') {
        stop = strucvar.start
      } else {
        stop = strucvar.stop
      }
      query =
        `?release=${release}&chromosome=${chrom}&start=${start}` +
        `&end=${stop}&sv_type=${svType}&sv_sub_type=${svType}`
    }

    return await this.fetchHelper(
      `/svs/ajax/structural-variant-flags/list-create/${caseUuid}/${query}`,
      'GET',
    )
  }

  async listProjectFlags(
    projectUuid: string,
    caseUuid?: string,
    strucvar?: Strucvar,
  ): Promise<SvFlags[]> {
    let query = ''
    if (strucvar) {
      const { svType, genomeBuild, chrom, start } = strucvar
      const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
      let stop
      if (svType === 'INS' || svType === 'BND') {
        stop = strucvar.start
      } else {
        stop = strucvar.stop
      }
      query =
        `?release=${release}&chromosome=${chrom}&start=${start}` +
        `&end=${stop}&sv_type=${svType}&sv_sub_type=${svType}`
    }
    if (caseUuid) {
      query += query
        ? `&exclude_case_uuid=${caseUuid}`
        : `?exclude_case_uuid=${caseUuid}`
    }
    return await this.fetchHelper(
      `/svs/ajax/structural-variant-flags/list-project/${projectUuid}/${query}`,
      'GET',
    )
  }

  async createFlags(
    caseUuid: string,
    strucvar: Strucvar,
    payload: SvFlags,
  ): Promise<SvFlags> {
    const { svType, genomeBuild, chrom, start } = strucvar
    const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
    let stop
    if (svType === 'INS' || svType === 'BND') {
      stop = strucvar.start
    } else {
      stop = strucvar.stop
    }
    const query =
      `release=${release}&chromosome=${chrom}&start=${start}` +
      `&end=${stop}&sv_type=${svType}&sv_sub_type=${svType}`
    return await this.fetchHelper(
      `/svs/ajax/structural-variant-flags/list-create/${caseUuid}/?${query}`,
      'POST',
      payload,
    )
  }

  async updateFlags(flagsUuid: string, payload: SvFlags): Promise<SvFlags> {
    return await this.fetchHelper(
      `/svs/ajax/structural-variant-flags/retrieve-update-destroy/${flagsUuid}/`,
      'PATCH',
      payload,
    )
  }

  async deleteFlags(flagsUuid: string) {
    return await this.fetchHelper(
      `/svs/ajax/structural-variant-flags/retrieve-update-destroy/${flagsUuid}/`,
      'DELETE',
    )
  }

  /** List acmg ratings for the given case, optionally for the given `sv`. */
  async listAcmgRating(
    caseUuid: string,
    strucvar?: Strucvar,
  ): Promise<SvAcmgRating[]> {
    let query = ''
    if (strucvar) {
      const { svType, genomeBuild, chrom, start } = strucvar
      const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
      let stop
      if (svType === 'INS' || svType === 'BND') {
        stop = strucvar.start
      } else {
        stop = strucvar.stop
      }
      query =
        `?release=${release}&chromosome=${chrom}&start=${start}` +
        `&end=${stop}&sv_type=${svType}&sv_sub_type=${svType}`
    }

    let nextUrl: string | null =
      `/svs/ajax/structural-variant-acmg-rating/list-create/${caseUuid}/${query}`
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

  async createAcmgRating(
    caseUuid: string,
    strucvar: Strucvar,
    payload: SvAcmgRating,
  ): Promise<SvAcmgRating> {
    const { svType, genomeBuild, chrom, start } = strucvar
    const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
    let stop
    if (svType === 'INS' || svType === 'BND') {
      stop = strucvar.start
    } else {
      stop = strucvar.stop
    }
    const query =
      `release=${release}&chromosome=${chrom}&start=${start}` +
      `&end=${stop}&sv_type=${svType}&sv_sub_type=${svType}`

    const result = (await this.fetchHelper(
      `/svs/ajax/structural-variant-acmg-rating/list-create/${caseUuid}/?${query}`,
      'POST',
      AcmgRating.toJson(payload),
    )) as AcmgRating$Api
    return AcmgRating.fromJson(result)
  }

  async updateAcmgRating(
    acmgRatingUuid: string,
    payload: SvAcmgRating,
  ): Promise<SvAcmgRating> {
    const result = (await this.fetchHelper(
      `/svs/ajax/structural-variant-acmg-rating/retrieve-update-destroy/${acmgRatingUuid}/`,
      'PATCH',
      AcmgRating.toJson(payload),
    )) as AcmgRating$Api
    return AcmgRating.fromJson(result)
  }

  async deleteAcmgRating(acmgRatingUuid: string) {
    return await this.fetchHelper(
      `/svs/ajax/structural-variant-acmg-rating/retrieve-update-destroy/${acmgRatingUuid}/`,
      'DELETE',
    )
  }

  async listProjectAcmgRating(
    projectUuid: string,
    caseUuid?: string,
    strucvar?: Strucvar,
  ): Promise<SvAcmgRating[]> {
    let query = ''
    if (strucvar) {
      const { svType, genomeBuild, chrom, start } = strucvar
      const release = genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38'
      let stop
      if (svType === 'INS' || svType === 'BND') {
        stop = strucvar.start
      } else {
        stop = strucvar.stop
      }
      query =
        `?release=${release}&chromosome=${chrom}&start=${start}` +
        `&end=${stop}&sv_type=${svType}&sv_sub_type=${svType}`
    }
    if (caseUuid) {
      query += query
        ? `&exclude_case_uuid=${caseUuid}`
        : `?exclude_case_uuid=${caseUuid}`
    }
    return await this.fetchHelper(
      `/svs/ajax/structural-variant-acmg-rating/list-project/${projectUuid}/${query}`,
      'GET',
    )
  }
}
