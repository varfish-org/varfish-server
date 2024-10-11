/** Conversion from three-letter to one-letter AA code. */
const THREE_LETTER_TO_ONE_LETTER = {
  Ala: 'A',
  Arg: 'R',
  Asn: 'N',
  Asp: 'D',
  Cys: 'C',
  Gln: 'Q',
  Glu: 'E',
  Gly: 'G',
  His: 'H',
  Ile: 'I',
  Leu: 'L',
  Lys: 'K',
  Met: 'M',
  Phe: 'F',
  Pro: 'P',
  Sec: 'U',
  Ser: 'S',
  Ter: '*',
  Thr: 'T',
  Trp: 'W',
  Tyr: 'Y',
  Val: 'V',
} as const

/**
 * Convert a three-letter amino acid code to a one-letter amino acid code.
 *
 * @param threeLetter - The three-letter amino acid code.
 * @returns The one-letter amino acid code.
 */
export const threeToOneAa = (threeLetter: string): string => {
  let result = threeLetter
  for (const [three, one] of Object.entries(THREE_LETTER_TO_ONE_LETTER)) {
    result = result.replace(three, one)
  }
  return result
}
