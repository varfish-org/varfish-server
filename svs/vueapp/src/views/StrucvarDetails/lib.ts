import { Strucvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'

// Pretty display of coordinates.
export const svLocus = (strucvar?: Strucvar): string | undefined => {
  if (strucvar === undefined) {
    return undefined
  }

  let locus: string = ''
  switch (strucvar.svType) {
    case 'INS':
      locus = `${strucvar.chrom}:${strucvar.start}-${strucvar.start}`
      break
    case 'DEL':
    case 'DUP':
    case 'INV':
      locus = `${strucvar.chrom}:${strucvar.start - 1000}-${strucvar.stop + 1000}`
      break
    case 'BND':
      locus = `${strucvar.chrom}:${strucvar.start - 1000}-${strucvar.start + 1000}`
      break
  }
  if (locus === '') {
    return undefined
  }

  if (strucvar.genomeBuild === 'grch38') {
    locus = `chr${locus}`
  }
  return locus
}
