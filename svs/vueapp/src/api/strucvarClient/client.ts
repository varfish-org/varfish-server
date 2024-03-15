import { ClientBase } from '@varfish/apiUtils'
import {
  QuickPresets,
  InheritancePresets,
  CategoryPresets,
  QuerySettingsShortcuts,
  CaseSvQuery,
  SvQueryResultSet,
  ListArgs,
  SvQueryResultRow,
  SvComment,
  SvFlags,
} from './types'
import { Strucvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'

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
}
