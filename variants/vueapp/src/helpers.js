import { computed } from 'vue'

export function copy(value) {
  return JSON.parse(JSON.stringify(value))
}

/**
 * Helper function to declare a wrapper around the props.
 *
 * @param props The props for the values.
 * @param key The name of the prop to wrap.
 * @param emit The emit to use for emitting update events.
 * @param mapper Mapping function that allows to convert string to integer, for example.
 * @param textOnly Boolean indicating whether to force convertion to String (e.g., to make happydom happy in tests)
 * @returns {WritableComputedRef<*>|*} Returns a {@code computed} value that will notify the parent about prop
 *          update via {@code emit}.
 */
export function declareWrapper(props, key, emit) {
  return computed({
    get() {
      if (key === 'qualMaxAd' && props[key] === 0) {
        return null
      }
      return props[key]
    },
    set(newValue) {
      if (key === 'qualMaxAd' && newValue === '') {
        newValue = 0
      }
      emit(`update:${key}`, newValue)
    },
  })
}

export const getAcmgBadge = (acmgClass) => {
  return acmgClass == null
    ? 'badge-light text-muted'
    : acmgClass > 3
    ? 'badge-danger text-white'
    : acmgClass === 3
    ? 'badge-warning text-black'
    : 'badge-success text-white'
}
