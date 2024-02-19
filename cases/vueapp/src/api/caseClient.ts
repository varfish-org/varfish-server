import { ClientBase } from '@varfish/apiUtils'

/**
 * Class for accessing the case REST API.
 */
export class CaseClient extends ClientBase {
  /** Retrieve case with the given UUID. */
  async retrieveCase(caseUuid: string) {
    return await this.fetchHelper(
      `/cases/ajax/case/retrieve-update-destroy/${caseUuid}/`,
      'GET',
    )
  }

  /** Update the case with the given UUID.
   *
   * @param caseUuid Case's UUID.
   * @param payload The JS object to submit as JSON.
   * @returns Promise with the updated case object.
   */
  async updateCase(caseUuid: string, payload: any): Promise<any> {
    return await this.fetchHelper(
      `/cases/ajax/case/retrieve-update-destroy/${caseUuid}/`,
      'PATCH',
      payload,
    )
  }

  /** Destroy the case with the given UUID.
   *
   * @param caseUuid Case's UUID.
   */
  async destroyCase(caseUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/cases/ajax/case/retrieve-update-destroy/${caseUuid}/`,
      'DELETE',
    )
  }

  /** List case comments. */
  async listCaseComment(caseUuid: string): Promise<any[]> {
    return await this.fetchHelper(
      `/cases/ajax/case-comment/list-create/${caseUuid}/`,
      'GET',
    )
  }

  /** Create CaseComment.
   *
   * @param caseUuid Case's UUID.
   * @param payload The JS object to submit as JSON.
   * @returns Promise with the updated Case object.
   */
  async createCaseComment(caseUuid: string, payload: any): Promise<any> {
    return await this.fetchHelper(
      `/cases/ajax/case-comment/list-create/${caseUuid}/`,
      'POST',
      payload,
    )
  }

  /** Retrieve CaseComment.
   *
   * @param caseCommentUuid UUID of the CaseComment
   * @returns Promise with the CaseComment object.
   */
  async retrieveCaseComment(caseCommentUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/cases/ajax/case-comment/retrieve-update-destroy/${caseCommentUuid}/`,
      'GET',
    )
  }

  /** Update CaseComment.
   *
   * @param caseCommentUuid UUID of the CaseComment to update.
   * @param payload Data to update the CaseComment with.
   * @returns Promise with the updated CaseComment data.
   */
  async updateCaseComment(caseCommentUuid: string, payload: any): Promise<any> {
    return await this.fetchHelper(
      `/cases/ajax/case-comment/retrieve-update-destroy/${caseCommentUuid}/`,
      'PATCH',
      payload,
    )
  }

  /** Delete CaseComment.
   *
   * @param caseCommentUuid UUID of the CaseComment to delete.
   */
  async destroyCaseComment(caseCommentUuid: string) {
    return await this.fetchHelper(
      `/cases/ajax/case-comment/retrieve-update-destroy/${caseCommentUuid}/`,
      'DELETE',
    )
  }

  /** Fetch all variant annotations for the given case. */
  async fetchVarAnnos(_caseUuid: string): Promise<Map<string, any>> {
    return Promise.resolve(new Map())
  }

  /** Fetch all SV annotations for the given case. */
  async fetchSvAnnos(_caseUuid: string): Promise<Map<string, any>> {
    return Promise.resolve(new Map())
  }

  /** Fetch all gene annotations */
  async fetchCaseGeneAnnotation(caseUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/cases/api/case-gene-annotation/list/${caseUuid}/`,
      'GET',
    )
  }

  /** Fetch case alignment stats. */
  async fetchCaseAlignmentStats(caseUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/cases/api/case-alignment-stats/list/${caseUuid}/`,
      'GET',
    )
  }

  /** Fetch case variant stats. */
  async fetchCaseVariantStats(caseUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/cases/api/case-variant-stats/list/${caseUuid}/`,
      'GET',
    )
  }

  /** Fetch case relatedness information. */
  async fetchCaseRelatedness(caseUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/cases/api/case-relatedness/list/${caseUuid}/`,
      'GET',
    )
  }

  /** Fetch case variant annotation release information. */
  async fetchAnnotationReleaseInfos(caseUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/cases/api/annotation-release-info/list/${caseUuid}/`,
      'GET',
    )
  }

  /** Fetch case SV annotation release information. */
  async fetchSvAnnotationReleaseInfos(caseUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/cases/api/sv-annotation-release-info/list/${caseUuid}/`,
      'GET',
    )
  }

  /** Fetch all case phenotype terms. */
  async listCasePhenotypeTerms(caseUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/cases/ajax/case-phenotype-terms/list-create/${caseUuid}/`,
      'GET',
    )
  }

  /** Create case phenotype terms object.
   *
   * @param caseUuid Case UUID to create for.
   * @param payload Data for the case phenotype terms object.
   * @returns Promise with the created object's data.
   */
  async createCasePhenotypeTerms(caseUuid: string, payload: any): Promise<any> {
    return await this.fetchHelper(
      `/cases/ajax/case-phenotype-terms/list-create/${caseUuid}/`,
      'POST',
      payload,
    )
  }

  /* Retrieve case phenotype terms.
   *
   * @param casePhenotypeTermsUuid UUID of case phenotype terms to retrieve.
   * @returns Promise with the case phenotype terms object.
   */
  async retrieveCasePhenotypeTerms(
    casePhenotypeTermsUuid: string,
  ): Promise<any> {
    return await this.fetchHelper(
      `/cases/ajax/case-phenotype-terms/retrieve-update-destroy/${casePhenotypeTermsUuid}/`,
      'GET',
    )
  }

  /** Update case phenotype terms.
   *
   * @param casePhenotypeTermsUuid UUID of the object to update.
   * @param payload Data to use for update.
   * @returns Updated object's data.
   */
  async updateCasePhenotypeTerms(
    casePhenotypeTermsUuid: string,
    payload: any,
  ): Promise<any> {
    return await this.fetchHelper(
      `/cases/ajax/case-phenotype-terms/retrieve-update-destroy/${casePhenotypeTermsUuid}/`,
      'PATCH',
      payload,
    )
  }

  /** Delete case phenotype terms object.
   *
   * @param casePhenotypeTermsUuid UUID of the object to delete.
   */
  async destroyCasePhenotypeTerms(casePhenotypeTermsUuid: string) {
    return await this.fetchHelper(
      `/cases/ajax/case-phenotype-terms/retrieve-update-destroy/${casePhenotypeTermsUuid}/`,
      'DELETE',
    )
  }
}
