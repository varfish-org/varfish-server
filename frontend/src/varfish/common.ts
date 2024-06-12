/**
 * Commonly used code.
 */

/**
 * Generate random string with a given length.
 *
 * This is meant to be used for generating unique identifiers for the DOM only but
 * not for anything application critical.
 *
 * @param len Length of string to create.
 * @returns Random string of given length.
 */
export function randomString(len: number): string {
  return (Math.random() + 1).toString(36).substring(len)
}
