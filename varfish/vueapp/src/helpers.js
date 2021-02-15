export function uuidv4 () {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

export function getSubmissionLabel (item) {
  if (item.variant_gene.length > 0 && item.variant_gene[0]) {
    if (item.variant_hgvs.length > 0 && item.variant_hgvs[0]) {
      return `${item.variant_gene[0]}:${item.variant_hgvs[0]}`
    } else {
      return `${item.variant_gene[0]}:<no hgvs>`
    }
  } else {
    return 'new variant'
  }
}

/**
 * Check current form for valid and display message or execute callback.
 *
 * @param cb Callback to call on success.
 * @param message Message to display for error notification.
 * @param title Title of error notification.
 * @returns {boolean} whether or not the currently displayed form was valid.
 */
export function validConfirmed (cb, message = 'Please fix the problems first.', title = 'invalid data') {
  if (!this.isValid()) {
    this.$bvModal.msgBoxOk(message, { title })
    return false
  } else {
    if (cb) {
      cb()
    }
    return true
  }
}
