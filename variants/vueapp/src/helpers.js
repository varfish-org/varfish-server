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
 * @returns {WritableComputedRef<*>|*} Returns a {@code computed} value that will notify the parent about prop
 *          update via {@code emit}.
 */
export function declareWrapper(props, key, emit, mapper) {
  return computed({
    get() {
      return props[key]
    },
    set(newValue) {
      if (mapper !== undefined) {
        newValue = mapper(newValue)
      }
      emit(`update:${key}`, newValue)
    },
  })
}

export const getAcmgBadge = (acmgClass) => {
  return acmgClass == null
    ? 'badge-outline-secondary text-muted'
    : acmgClass > 3
    ? 'badge-danger text-white'
    : acmgClass === 3
    ? 'badge-warning text-black'
    : 'badge-success text-white'
}
