import { ClientBase } from '@varfish/apiUtils'

type QuickPresets = any
type InheritancePresets = any
type CategoryPresets = any
type QuerySettingsShortcuts = any
type CaseSvQuery = any
type SvQueryResultSet = any
type SvQueryResultRow = any
type SvComment = any
type SvFlags = any

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
  async listComment(caseUuid: string, sv?: StructuralVariant) {
    let query = ''
    if (sv) {
      const { release, chromosome, start, end, sv_type, sv_sub_type } = sv
      query =
        `?release=${release}&chromosome=${chromosome}&start=${start}` +
        `&end=${end}&sv_type=${sv_type}&sv_sub_type=${sv_sub_type}`
    }

    return await this.fetchHelper(
      `/svs/ajax/structural-variant-comment/list-create/${caseUuid}/${query}`,
      'GET',
    )
  }

  async createComment(
    caseUuid: string,
    sv: StructuralVariant,
    payload: SvComment,
  ): Promise<SvComment> {
    const { release, chromosome, start, end, sv_type, sv_sub_type } = sv
    const query =
      `release=${release}&chromosome=${chromosome}&start=${start}` +
      `&end=${end}&sv_type=${sv_type}&sv_sub_type=${sv_sub_type}`

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
  async listFlags(
    caseUuid: string,
    sv?: StructuralVariant,
  ): Promise<SvFlags[]> {
    let query = ''
    if (sv) {
      const { release, chromosome, start, end, sv_type, sv_sub_type } = sv
      query =
        `?release=${release}&chromosome=${chromosome}&start=${start}` +
        `&end=${end}&sv_type=${sv_type}&sv_sub_type=${sv_sub_type}`
    }

    return await this.fetchHelper(
      `/svs/ajax/structural-variant-flags/list-create/${caseUuid}/${query}`,
      'GET',
    )
  }

  async createFlags(
    caseUuid: string,
    sv: StructuralVariant,
    payload: SvFlags,
  ): Promise<SvFlags> {
    const { release, chromosome, start, end, sv_type, sv_sub_type } = sv
    const query =
      `release=${release}&chromosome=${chromosome}&start=${start}` +
      `&end=${end}&sv_type=${sv_type}&sv_sub_type=${sv_sub_type}`
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
