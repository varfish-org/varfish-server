// Wait for ag-grid to be ready
// Adapted from: https://www.ag-grid.com/javascript-grid-testing-vue/
// TODO: Handle reject
// TODO: Improve
export const waitAG = (wrapper) =>
  new Promise(function (resolve, _reject) {
    ;(function waitForGridReady() {
      if (wrapper.find('.ag-row')) return resolve()
      setTimeout(waitForGridReady, 10)
    })()
  })

export const waitRAF = () =>
  new Promise((resolve) => requestAnimationFrame(resolve))

export const quoteattr = (s, preserveCR) => {
  preserveCR = preserveCR ? '&#13;' : '\n'
  return (
    ('' + s) /* Forces the conversion to string. */
      .replace(/&/g, '&amp;') /* This MUST be the 1st replacement. */
      .replace(/'/g, '&apos;') /* The 4 other predefined entities, required. */
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      /*
        You may add other replacements here for HTML only
        (but it's not necessary).
        Or for XML, only if the named entities are defined in its DTD.
        */
      .replace(/\r\n/g, preserveCR) /* Must be before the next replacement. */
      .replace(/[\r\n]/g, preserveCR)
  )
}
