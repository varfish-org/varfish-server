import { ClientBase } from '@varfish/apiUtils'
import { VarfishStats } from '@cases_qc/api/types'

/**
 * Class for accessing the case REST API.
 */
export class CaseQcClient extends ClientBase {
  /** Retrieve ``CaseQc`` for case with the given UUID. */
  async retrieveCaseQc(caseUuid: string) {
    return await this.fetchHelper(
      `/cases-qc/api/caseqc/retrieve/${caseUuid}/`,
      'GET',
    )
  }

  /** Retrieve ``VarfishStats`` for case with the given UUID. */
  async retrieveVarfishStats(caseUuid: string): Promise<VarfishStats> {
    return await this.fetchHelper(
      `/cases-qc/api/varfishstats/retrieve/${caseUuid}/`,
      'GET',
    )
  }
}
