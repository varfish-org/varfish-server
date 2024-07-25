/**
 * Enumeration for preset set version states.
 */
export enum PresetSetVersionState {
  ACTIVE = 'active',
  DRAFT = 'draft',
  RETIRED = 'retired',
}

/**
 * Enumerations for representing that a presets version is editable or the reason
 * why it is not.
 */
export enum EditableState {
  EDITABLE,
  IS_ACTIVE,
  IS_RETIRED,
  IS_FACTORY_DEFAULT,
  IS_NOT_SET,
}

/**
 * Return user-readable string for the editable state.
 */
export const getEditableStateLabel = (state: EditableState): string => {
  let token = ''
  switch (state) {
    case EditableState.EDITABLE:
      return (
        'This preset set version is in draft state and thus editable. ' +
        'You will need to activate it to make it useable in queries.'
      )
    case EditableState.IS_ACTIVE:
      token = 'active'
      break
    case EditableState.IS_RETIRED:
      token = 'retired'
      break
    case EditableState.IS_FACTORY_DEFAULT:
      token = 'a factory default'
      break
    case EditableState.IS_NOT_SET:
      return 'Preset set is currently unset.'
  }
  return (
    `This preset set version is ${token} and thus not editable. ` +
    'You need to create a new draft version, make changes there, ' +
    'and then activate it to make it useable in queries.'
  )
}
