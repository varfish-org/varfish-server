const MEHARI_BASE_URL = '/proxy/varfish/mehari'

export class MehariApiClient {
  baseUrl: string
  csrfToken?: string

  constructor(csrfToken?: string, baseUrl?: string) {
    this.csrfToken = csrfToken
    this.baseUrl = baseUrl ?? MEHARI_BASE_URL
  }

  /**
   * Retrieve transcript consequence information via mehari REST API.
   */
  async retrieveTxCsq(
    genomeRelease: string,
    chromosome: string,
    pos: number,
    reference: string,
    alternative: string,
    hgncId?: string,
  ): Promise<any> {
    const hgncSuffix = hgncId ? `&hgnc_id=${hgncId}` : ''
    const url =
      `${this.baseUrl}/seqvars/csq?genome_release=${genomeRelease}&` +
      `chromosome=${chromosome}&position=${pos}&reference=${reference}&` +
      `alternative=${alternative}${hgncSuffix}`

    const headers: { [key in string]: string } = {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    }
    if (this.csrfToken) {
      headers['X-CSRFToken'] = this.csrfToken
    }

    const response = await fetch(url, {
      method: 'GET',
      credentials: 'same-origin',
      headers,
    })

    return await response.json()
  }
}
