import { Strucvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { igvLocus } from '@bihealth/reev-frontend-lib/lib/utils'

/**
 * Jump to the locus in the local IGV.
 */
export const jumpToLocus = async (strucvar?: Strucvar) => {
  if (strucvar === undefined) {
    return
  }
  // NB: for breakends this is a space-delimited list of both breakpoints, which makes IGV
  // open its split-screen view.  The space is percent-encoded by the URL parser in `fetch`.
  const url = `http://127.0.0.1:60151/goto?locus=${igvLocus(strucvar)}`
  // NB: we allow the call to fetch here as it goes to local IGV.
  await fetch(url).catch((e) => {
    const msg =
      "Couldn't connect to IGV. Please make sure IGV is running and try again."
    alert(msg)
    console.error(msg, e)
  })
}
