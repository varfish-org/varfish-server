import { computed } from 'vue'

export function displayName(name) {
  if (name) {
    const re = /-N\d+-(DNA|RNA)\d+-(WES|WGS)\d+$/
    return name.replace(re, '')
  } else {
    return name
  }
}

/**
 * Helper function to declare a wrapper around the props.
 *
 * @param props The props for the values.
 * @param key The name of the prop to wrap.
 * @param emit The emit to use for emitting update events.
 * @returns {WritableComputedRef<*>|*} Returns a {@code computed} value that will notify the parent about prop
 *          update via {@code emit}.
 */
export function declareWrapper(props, key, emit) {
  return computed({
    get() {
      return props[key]
    },
    set(newValue) {
      emit(`update:${key}`, newValue)
    },
  })
}
