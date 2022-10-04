'use strict'
var __importDefault =
  (this && this.__importDefault) ||
  function (mod) {
    return mod && mod.__esModule ? mod : { default: mod }
  }
Object.defineProperty(exports, '__esModule', { value: true })
const DOMException_1 = __importDefault(require('../../exception/DOMException'))
const DOMExceptionNameEnum_1 = __importDefault(
  require('../../exception/DOMExceptionNameEnum')
)
const HTMLElement_1 = __importDefault(require('../html-element/HTMLElement'))
const ValidityState_1 = __importDefault(
  require('../validity-state/ValidityState')
)
const HTMLOptionsCollection_1 = __importDefault(
  require('../html-option-element/HTMLOptionsCollection')
)
const HTMLSelectElementValueSanitizer_1 = __importDefault(
  require('./HTMLSelectElementValueSanitizer')
)
/**
 * HTML Select Element.
 *
 * Reference:
 * https://developer.mozilla.org/en-US/docs/Web/API/HTMLSelectElement.
 */
class HTMLSelectElement extends HTMLElement_1.default {
  constructor() {
    super(...arguments)
    this._value = null
    this._selectedIndex = -1
    this._options = null
  }
  /**
   * Returns name.
   *
   * @returns Name.
   */
  get name() {
    return this.getAttributeNS(null, 'name') || ''
  }
  /**
   * Sets name.
   *
   * @param name Name.
   */
  set name(name) {
    this.setAttributeNS(null, 'name', name)
  }
  /**
   * Returns disabled.
   *
   * @returns Disabled.
   */
  get disabled() {
    return this.getAttributeNS(null, 'disabled') !== null
  }
  /**
   * Sets disabled.
   *
   * @param disabled Disabled.
   */
  set disabled(disabled) {
    if (!disabled) {
      this.removeAttributeNS(null, 'disabled')
    } else {
      this.setAttributeNS(null, 'disabled', '')
    }
  }
  /**
   * Returns multiple.
   *
   * @returns Multiple.
   */
  get multiple() {
    return this.getAttributeNS(null, 'multiple') !== null
  }
  /**
   * Sets multiple.
   *
   * @param multiple Multiple.
   */
  set multiple(multiple) {
    if (!multiple) {
      this.removeAttributeNS(null, 'multiple')
    } else {
      this.setAttributeNS(null, 'multiple', '')
    }
  }
  /**
   * Returns autofocus.
   *
   * @returns Autofocus.
   */
  get autofocus() {
    return this.getAttributeNS(null, 'autofocus') !== null
  }
  /**
   * Sets autofocus.
   *
   * @param autofocus Autofocus.
   */
  set autofocus(autofocus) {
    if (!autofocus) {
      this.removeAttributeNS(null, 'autofocus')
    } else {
      this.setAttributeNS(null, 'autofocus', '')
    }
  }
  /**
   * Returns required.
   *
   * @returns Required.
   */
  get required() {
    return this.getAttributeNS(null, 'required') !== null
  }
  /**
   * Sets required.
   *
   * @param required Required.
   */
  set required(required) {
    if (!required) {
      this.removeAttributeNS(null, 'required')
    } else {
      this.setAttributeNS(null, 'required', '')
    }
  }
  /**
   * Returns value.
   *
   * @returns Value.
   */
  get value() {
    return this._value
  }
  /**
   * Sets value.
   *
   * @param value Value.
   */
  set value(value) {
    this._value = HTMLSelectElementValueSanitizer_1.default.sanitize(value)
    const idx = this.options.findIndex((o) => o.nodeValue === value)
    if (idx > -1) {
      this._selectedIndex = idx
    }
  }
  /**
   * Returns value.
   *
   * @returns Value.
   */
  get selectedIndex() {
    return this._options ? this._options.selectedIndex : -1
  }
  /**
   * Sets value.
   *
   * @param value Value.
   */
  set selectedIndex(value) {
    if (value > this.options.length - 1 || value < 0) {
      throw new DOMException_1.default(
        'Select elements selected index must be valid',
        DOMExceptionNameEnum_1.default.indexSizeError
      )
    }
    this._options.selectedIndex = value
  }
  /**
   * Returns the parent form element.
   *
   * @returns Form.
   */
  get form() {
    let parent = this.parentNode
    while (parent && parent.tagName !== 'FORM') {
      parent = parent.parentNode
    }
    return parent
  }
  /**
   * Returns validity state.
   *
   * @returns Validity state.
   */
  get validity() {
    return new ValidityState_1.default(this)
  }
  /**
   * Returns "true" if it will validate.
   *
   * @returns "true" if it will validate.
   */
  get willValidate() {
    return (
      this.type !== 'hidden' &&
      this.type !== 'reset' &&
      this.type !== 'button' &&
      !this.disabled &&
      !this['readOnly']
    )
  }
  /**
   * Returns options.
   *
   * @returns Options.
   */
  get options() {
    if (this._options === null) {
      this._options = new HTMLOptionsCollection_1.default()
      const childs = this.childNodes
      for (const child of childs) {
        if (child.tagName === 'OPTION') {
          this._options.add(child)
        }
      }
    }
    return this._options
  }
}
exports.default = HTMLSelectElement
//# sourceMappingURL=HTMLSelectElement.js.map
