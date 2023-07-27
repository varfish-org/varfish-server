import { chunks } from '@reactgular/chunks'

const ANNONARS_BASE_URL = '/proxy/varfish/annonars'
const DEFAULT_CHUNK_SIZE = 100

export class AnnonarsApiClient {
  baseUrl: string
  defaultChunkSize: number
  csrfToken?: string

  constructor(csrfToken?: string, defaultChunkSize?: number, baseUrl?: string) {
    this.csrfToken = csrfToken
    this.baseUrl = baseUrl ?? ANNONARS_BASE_URL
    this.defaultChunkSize = defaultChunkSize ?? DEFAULT_CHUNK_SIZE
  }

  /**
   * Retrieve gene information via annonars REST API.
   *
   * @param hgncIds Array of HGNC IDs to use, e.g., `["HGNC:26467"]`.
   * @param chunkSize How many IDs to send in one request.
   * @returns Promise with an array of gene information objects.
   */
  async retrieveGeneInfos(
    hgncIds: Array<string>,
    chunkSize?: number
  ): Promise<Array<any>> {
    const hgncIdChunks = chunks(hgncIds, chunkSize ?? this.defaultChunkSize)

    const promises = hgncIdChunks.map((chunk) => {
      const url = `${this.baseUrl}/genes/info?hgnc-id=${chunk.join(',')}`

      const headers = {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      }
      if (this.csrfToken) {
        headers['X-CSRFToken'] = this.csrfToken
      }

      return fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers,
      })
    })

    const responses = await Promise.all(promises)
    const results = await Promise.all(
      responses.map((response) => response.json())
    )

    const result = []
    results.forEach((chunk) => {
      for (const value of Object.values(chunk.genes)) {
        result.push(value)
      }
    })
    return result
  }

  /**
   * Retrieve variant information via annonars REST API.
   */
  async retrieveVariantAnnos(
    genomeRelease: string,
    chromosome: string,
    pos: number,
    reference: string,
    alternative: string
  ): Promise<any> {
    const url =
      `${this.baseUrl}/annos/variant?genome-release=${genomeRelease}&` +
      `chromosome=${chromosome}&pos=${pos}&reference=${reference}&` +
      `alternative=${alternative}`

    const headers = {
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
