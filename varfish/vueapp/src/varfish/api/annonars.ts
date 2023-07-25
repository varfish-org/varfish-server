import { chunks } from '@reactgular/chunks'

const ANNONARS_BASE_URL = '/proxy/varfish/annonars'

export default {
  /**
   * Retrieve gene information via annonars REST API.
   *
   * @param hgncIds Array of HGNC IDs to use, e.g., `["HGNC:26467"]`.
   * @param chunkSize How many IDs to send in one request.
   * @returns Promise with an array of gene information objects.
   */
  async retrieveGeneInfos(
    hgncIds: Array<string>,
    chunkSize: number = 100
  ): Promise<Array<any>> {
    const hgncIdChunks = chunks(hgncIds, chunkSize)

    const promises = hgncIdChunks.map((chunk) => {
      const url = `${ANNONARS_BASE_URL}/genes/info?hgnc-id=${chunk.join(',')}`

      return fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
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
  },
}
