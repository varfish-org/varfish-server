/**
 * Helper store that allows user to manipulate the UIs.
 */

import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUiStore = defineStore('ui', () => {
  /** Whether the UI is maximized */
  const maximized = ref<boolean>(false)

  /** The original margin */
  const origMargin = ref<any>(null)

  const toggleMaximised = () => {
    maximized.value = !maximized.value

    const dispValue = maximized.value ? 'none' : 'block'
    const elementIdsToggle = [
      'sodar-content-left',
      'sodar-sub-navbar-container',
    ]

    elementIdsToggle.forEach((elementId) => {
      document.getElementById(elementId).style.display = dispValue
    })

    const elementIdMargin = 'sodar-app-content'
    if (origMargin.value === null) {
      origMargin.value = document.getElementById(elementIdMargin).style.padding
    }
    if (maximized.value) {
      document.getElementById(elementIdMargin).style.padding = '14px'
    } else {
      document.getElementById(elementIdMargin).style.padding = origMargin.value
    }
  }

  return {
    // state
    maximized,
    // functions
    toggleMaximised,
  }
})
