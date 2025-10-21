import { ClientBase } from '@/varfish/apiUtils'

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
 * Class for accessing the case list ("all cases for a project") REST API.
 */
export class CaseListClient extends ClientBase {
  /**
   * Access to cases in the given project
   *
   * @param projectUuid UUID of the given project.
   * @param args Query arguments.
   * @returns Promise with an array of the cases.
   */
  async listCase(projectUuid: string, args: ListArgs): Promise<any> {
    const { pageNo, pageSize, orderBy, orderDir, queryString } = args
    const queryArr: string[] = []
    if (pageNo !== undefined && pageNo !== null) {
      queryArr.push(`page=${pageNo + 1}`)
    }
    if (pageSize !== undefined && pageSize !== null) {
      queryArr.push(`page_size=${pageSize}`)
    }
    if (orderBy !== undefined && orderBy !== null) {
      queryArr.push(`order_by=${orderBy}`)
    }
    if (orderDir !== undefined && orderDir !== null) {
      queryArr.push(`order_dir=${orderDir}`)
    }
    if ((queryString?.length ?? 0) > 0) {
      queryArr.push(`q=${queryString}`)
    }
    const queryStr = queryArr.length ? '?' + queryArr.join('&') : ''

    return await this.fetchHelper(
      `/cases/ajax/case/list/${projectUuid}/${queryStr}`,
      'GET',
    )
  }

  /**
   * Retrieve project information.
   *
   * @param projectUuid UUID of the project to query for.
   * @returns Promise with project information.
   */
  async fetchProject(projectUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/project/api/retrieve/${projectUuid}`,
      'GET',
      null,
      {
        accept: 'application/vnd.bihealth.sodar-core.projectroles+json',
      },
    )
  }

  /**
   * Retrieve current user's permissions to the given project.
   *
   * @param projectUuid UUID of project to query for.
   * @returns Promise with permission information.
   */
  async fetchPermissions(projectUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/cases/ajax/user-permissions/${projectUuid}/`,
      'GET',
    )
  }

  /**
   * Retrieve project QC values.
   *
   * @param projectUid UUID of the project.
   * @returns Promise with the QC values of the project.
   */
  async loadProjectQcValues(projectUuid: string): Promise<any> {
    return await this.fetchHelper(
      `/variants/ajax/project/qc/${projectUuid}/`,
      'GET',
    )
  }

  fetchVarComments(_projectUuid: string) {
    console.warn('fetchVarComments not implemented yet')
    return Promise.resolve([])
  }

  fetchVarAcmgRatings(_projectUuid: string) {
    console.warn('fetchVarAcmgRatings not implemented yet')
    return Promise.resolve([])
  }

  fetchSvAnnos(_projectUuid: string) {
    console.warn('fetchSvAnnos not implemented yet')
    return Promise.resolve([])
  }

  fetchSvComments(_projectUuid: string) {
    console.warn('fetchSvComments not implemented yet')
    return Promise.resolve([])
  }
}
