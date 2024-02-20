/**
 * Helper store that allows user to manipulate the UIs.
 */

import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUiStore = defineStore('ui', () => {
  /** Whether the UI is maximized */
  const maximized = ref<boolean>(false)

  /** The original margin */
  const origMargin = ref<string>('')

  const toggleMaximised = () => {
    maximized.value = !maximized.value

    const dispValue = maximized.value ? 'none' : 'block'
    const elementIdsToggle = [
      'sodar-content-left',
      'sodar-sub-navbar-container',
    ]

    elementIdsToggle.forEach((elementId) => {
      const element = document.getElementById(elementId)
      if (element) {
        element.style.display = dispValue
      }
    })

    const elementIdMargin = 'sodar-app-content'
    const elementMargin = document.getElementById(elementIdMargin)
    if (elementMargin) {
      if (origMargin.value === null) {
        origMargin.value = elementMargin.style.padding
      }
      if (maximized.value) {
        elementMargin.style.padding = '14px'
      } else {
        elementMargin.style.padding = origMargin.value
      }
    }
  }

  return {
    // state
    maximized,
    // functions
    toggleMaximised,
  }
})
