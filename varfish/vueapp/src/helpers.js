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

export function removeItemOnce (arr, value) {
  const index = arr.indexOf(value)
  if (index > -1) {
    arr.splice(index, 1)
  }
  return arr
}

export function removeItemAll (arr, value) {
  let i = 0
  while (i < arr.length) {
    if (arr[i] === value) {
      arr.splice(i, 1)
    } else {
      ++i
    }
  }
  return arr
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

export function isDiseaseTerm (termId) {
  return termId.startsWith('OMIM:') || termId.startsWith('ORPHA:')
}

export const HPO_INHERITANCE_MODE = Object.freeze(new Map([
  ['HP:0001452', 'Autosomal dominant contiguous gene syndrome'],
  ['HP:0025352', 'Autosomal dominant germline de novo mutation'],
  ['HP:0000006', 'Autosomal dominant inheritance'],
  ['HP:0012275', 'Autosomal dominant inheritance with maternal imprinting'],
  ['HP:0012274', 'Autosomal dominant inheritance with paternal imprinting'],
  ['HP:0001444', 'Autosomal dominant somatic cell mutation'],
  ['HP:0000007', 'Autosomal recessive inheritance'],
  ['HP:0001466', 'Contiguous gene syndrome'],
  ['HP:0010984', 'Digenic inheritance'],
  ['HP:0003743', 'Genetic anticipation'],
  ['HP:0003744', 'Genetic anticipation with paternal anticipation bias'],
  ['HP:0010985', 'Gonosomal inheritance'],
  ['HP:0001475', 'Male-limited autosomal dominant'],
  ['HP:0001427', 'Mitochondrial inheritance'],
  ['HP:0001426', 'Multifactorial inheritance'],
  ['HP:0010983', 'Oligogenic inheritance'],
  ['HP:0010982', 'Polygenic inheritance'],
  ['HP:0032113', 'Semidominant mode of inheritance'],
  ['HP:0001470', 'Sex-limited autosomal dominant'],
  ['HP:0031362', 'Sex-limited autosomal recessive inheritance'],
  ['HP:0001442', 'Somatic mosaicism'],
  ['HP:0001428', 'Somatic mutation'],
  ['HP:0003745', 'Sporadic'],
  ['HP:0032382', 'Uniparental disomy'],
  ['HP:0032383', 'Uniparental heterodisomy'],
  ['HP:0032384', 'Uniparental isodisomy'],
  ['HP:0001423', 'X-linked dominant inheritance'],
  ['HP:0001417', 'X-linked inheritance'],
  ['HP:0001419', 'X-linked recessive inheritance']
]))
export const HPO_AGE_OF_ONSET = Object.freeze(new Map([
  ['HP:0030674', 'Antenatal'],
  ['HP:0011460', 'Embryonal'],
  ['HP:0011461', 'Fetal'],
  ['HP:0410280', 'Pediatric'],
  ['HP:0003593', 'Infantile'],
  ['HP:0011405', 'Childhood'],
  ['HP:0003621', 'Juvenile'],
  ['HP:0003581', 'Adult'],
  ['HP:0003623', 'Neonatal'],
  ['HP:0011462', 'Young adult'],
  ['HP:0003596', 'Middle age'],
  ['HP:0003584', 'Late'],
  ['HP:0003577', 'Congenital']
]))
