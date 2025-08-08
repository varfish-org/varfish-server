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
 * Convert all three-letter amino acid codes one-letter amino acid codes in a string.
 * This is not limited to a protein string as we also want to be able to process
 * HGVS strings.
 *
 * @param threeLetter - The three-letter amino acid code.
 * @returns The one-letter amino acid code.
 */
export const threeToOneAa = (threeLetter: string): string => {
  const regex = new RegExp(
    Object.keys(THREE_LETTER_TO_ONE_LETTER).join('|'),
    'g',
  )
  return threeLetter.replace(
    regex,
    (match) =>
      THREE_LETTER_TO_ONE_LETTER[
        match as keyof typeof THREE_LETTER_TO_ONE_LETTER
      ],
  )
}
