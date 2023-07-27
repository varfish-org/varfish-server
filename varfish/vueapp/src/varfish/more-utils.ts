/**
 * Round `value` to `digits` and return an `<abbr>` tag that has the original value
 * as the `@title` and the rounded value as the inner text.  Optionally add a `label`
 * to the `@title`
 *
 * @param value  The value to use and round.
 * @param digits The number of digits to round to.
 * @param label  The optional label to add.
 */
export const roundIt = (
  value: number,
  digits: number = 2,
  label?: string
): string => {
  if (!value) {
    return `<abbr title='${value}'>NaN</abbr>`
  }
  const roundedValue = value.toFixed(digits)
  const useLabel = label ? `${label}: ` : ''
  return `<abbr title="${useLabel}${value}">${roundedValue}</abbr>`
}

/**
 * Converts a number to a string with thousands separator.
 *
 * @param value     The number to separate.
 * @param separator The separator to use.
 */
export const separateIt = (value: number, separator: string = ' '): string => {
  const asString = `${value}`
  if (!asString.length) {
    return '0'
  }
  const splitString = asString.split('.', 1)
  const cardinal = splitString[0]
  if (!cardinal?.length) {
    splitString[0] = '0'
  } else {
    const offset = cardinal.length % 3
    const arr = [cardinal.slice(0, offset)]
    for (let i = 0; i <= cardinal.length; i += 3) {
      arr.push(cardinal.slice(offset + i, offset + i + 3))
    }
    splitString[0] = arr.join(' ')
  }
  return splitString.join('.')
}

/**
 * Returns whether the given variant looks mitochondrial.
 * @param smallVar Small variant to check.
 * @returns whether the position is on the mitochondrial genome
 */
export const isVariantMt = (smallVar): boolean => {
  return ['MT', 'M', 'chrMT', 'chrM'].includes(smallVar?.chromosome)
}

/**
 * Returns whether the given position is in a homopolymer on the mitochondrial chromosome.
 *
 * @param smallVar Small variant to check.
 * @returns whether the position is in a mitochondrial homopolymer
 */
export const isVariantMtHomopolymer = (smallVar): boolean => {
  if (!smallVar) {
    return false
  }
  const { chromosome, start, end } = smallVar
  const positionCheck = (pos) => {
    return (
      (pos >= 66 && pos <= 71) ||
      (pos >= 300 && pos <= 316) ||
      (pos >= 513 && pos <= 525) ||
      (pos >= 3106 && pos <= 3107) ||
      (pos >= 12418 && pos <= 12425) ||
      (pos >= 16182 && pos <= 16194)
    )
  }
  if (isVariantMt(smallVar)) {
    return positionCheck(start) || positionCheck(end)
  }
}
