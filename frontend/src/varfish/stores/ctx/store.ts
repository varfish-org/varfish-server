import { ref } from 'vue'
import { defineStore } from 'pinia'
import { SodarUser } from './types'
import {
  CasesService,
  UserAndGlobalSettings,
} from '@varfish-org/varfish-api/lib'

/**
 * Returns the value of a cookie.
 *
 * @param name The name of the cookie.
 * @returns The value of the cookie.
 */
const getCookie = (name: string): string | undefined => {
  const nameLenPlus = name.length + 1
  return (
    document.cookie
      .split(';')
      .map((c) => c.trim())
      .filter((cookie) => {
        return cookie.substring(0, nameLenPlus) === `${name}=`
      })
      .map((cookie) => {
        return decodeURIComponent(cookie.substring(nameLenPlus))
      })[0] || undefined
  )
}

/**
 * Helper store that provides global context.
 *
 * Currently, this is:
 *
 * - Current user information
 * - CSRF token
 */
export const useCtxStore = defineStore('ctx', () => {
  /** The CSRF token. */
  const csrfToken = ref<string>('')
  /** The current user. */
  const currentUser = ref<SodarUser | undefined>(undefined)
  /** The current global and user settings. */
  const userAndGlobalSettings = ref<UserAndGlobalSettings | undefined>(
    undefined,
  )

  /**
   * Initialize the store with CSRF token and project UUID.
   *
   * @param force Whether to force re-initialization.
   */
  const initialize = async (force: boolean = false) => {
    if (csrfToken.value !== '' && !force) {
      return
    }

    setupCsrfToken()
    await Promise.all([loadUser(), loadUserAndGlobalSettings()])
  }

  /**
   * Load the current user.
   */
  const loadUser = async () => {
    const response = await fetch('/project/api/users/current', {
      method: 'GET',
    })

    if (response.ok) {
      const data = await response.json()
      currentUser.value = data as SodarUser
    } else {
      throw new Error('Failed to load current user')
    }
  }

  /**
   * Load the current user and global settings.
   */
  const loadUserAndGlobalSettings = async () => {
    const response = await CasesService.casesApiUserAndGlobalSettingsRetrieve()
    if (response.data) {
      userAndGlobalSettings.value = response.data
    }
  }

  /**
   * Setup the CSRF token.
   *
   * This will make another request for the "user and global settings" and
   * look at the "csrftoken" response cookie.  This is necessary as the
   * heyapi wrapper does not give us access.
   */
  const setupCsrfToken = async () => {
    csrfToken.value = getCookie('csrftoken') || ''
  }

  return {
    // attributes
    csrfToken,
    currentUser,
    userAndGlobalSettings,
    // methods
    initialize,
  }
})
