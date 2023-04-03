import { apiFetch } from '@varfish/api-utils.js'

export default {
  async retrieveGeneInfos(
    csrfToken,
    database,
    geneId,
    ensemblTranscriptId = null
  ) {
    const suffix = ensemblTranscriptId
      ? `?ensembl_transcript_id=${ensemblTranscriptId}`
      : ''
    const response = await apiFetch(
      csrfToken,
      `/geneinfo/api/gene-infos/${database}/${geneId}/${suffix}`,
      'GET'
    )
    return await response.json()
  },
}
