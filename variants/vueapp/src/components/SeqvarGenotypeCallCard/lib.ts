import { GenotypeValue } from './types'

export const allelicBalance = (value?: GenotypeValue) => {
  if (!value || !value?.dp || !value?.ad) {
    return 0.0
  } else {
    return value.ad / value.dp
  }
}
