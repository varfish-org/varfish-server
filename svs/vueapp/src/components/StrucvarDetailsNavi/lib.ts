import { Strucvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'

/**
 * Jump to the locus in the local IGV.
 */
export const jumpToLocus = async (strucvar?: Strucvar) => {
  if (strucvar === undefined) {
    return
  }
  let url: string
  let chrom = strucvar.chrom
  if (chrom?.startsWith('chr')) {
    chrom = chrom.slice(3)
  }
  if (strucvar.svType === 'BND' || strucvar.svType === 'INS') {
    url = `http://127.0.0.1:60151/goto?locus=${chrom}:${strucvar.start ?? 1}-${(strucvar.start ?? 1) + 1}`
  } else {
    url = `http://127.0.0.1:60151/goto?locus=${chrom}:${strucvar.start ?? 1}-${strucvar.stop ?? strucvar.start ?? 1}`
  }
  // NB: we allow the call to fetch here as it goes to local IGV.
  await fetch(url).catch((e) => {
    const msg =
      "Couldn't connect to IGV. Please make sure IGV is running and try again."
    alert(msg)
    console.error(msg, e)
  })
}
