import { Seqvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'

/**
 * Jump to the locus in the local IGV.
 */
export const jumpToLocus = async (seqvar?: Seqvar) => {
  // NB: we allow the call to fetch here as it goes to local IGV.
  let chrom = seqvar?.chrom
  if (chrom?.startsWith('chr')) {
    chrom = chrom.slice(3)
  }
  await fetch(
    `http://127.0.0.1:60151/goto?locus=${chrom}:${seqvar?.pos}-${
      (seqvar?.pos ?? 0) + (seqvar?.del?.length ?? 0)
    }`,
  ).catch((e) => {
    const msg =
      "Couldn't connect to IGV. Please make sure IGV is running and try again."
    alert(msg)
    console.error(msg, e)
  })
}
