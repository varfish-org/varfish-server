import { ref } from 'vue'
import { defineStore } from 'pinia'

/**
 * Helper store that allows us to store a stack of the history.
 *
 * Implements behaviour that the initial push to the initial location is ignored.
 */
export const useHistoryStore = defineStore('history', () => {
  /** Whether the initial element was skipped already. */
  const initialSkipped = ref<boolean>(false)

  /** Browser history elements. */
  const elements = ref<any[]>([])

  /**
   * Push a history element to the stack.
   *
   * This is done in an router event handler to keep track of the history.
   */
  const pushPath = (element: any) => {
    if (initialSkipped.value) {
      elements.value.push(element)
    } else {
      initialSkipped.value = true
    }
  }

  /**
   * Returns last history element that has a `name` property different from `name` parameter.
   *
   * @param name The name to filter for.
   * @returns History element.
   */
  const lastWithDifferentName = (name: string): any | null => {
    for (const element of elements.value.slice().reverse()) {
      if (element.name !== name) {
        return element
      }
    }
    return null
  }

  return {
    // state
    initialSkipped,
    elements,
    // functions
    pushPath,
    lastWithDifferentName,
  }
})
