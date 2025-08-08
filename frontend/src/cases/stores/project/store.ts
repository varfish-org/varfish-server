import {
  Project,
  projectApiRetrieveRetrieve,
} from '@varfish-org/varfish-api/lib'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { client } from '@/cases/plugins/heyApi'

/**
 * Store to provide information on the current project.
 */
export const useProjectStore = defineStore('project', () => {
  // attributes
  /** The project UUID. */
  const projectUuid = ref<string | undefined>(undefined)
  /** The project loaded from API. */
  const project = ref<Project | undefined>(undefined)

  /**
   * Initialize the store with CSRF token and project UUID.
   *
   * @param projectUuid$ The project UUID.
   * @param force Whether to force re-initialization.
   */
  const initialize = async (projectUuid$?: string, force: boolean = false) => {
    if (projectUuid.value === projectUuid$ && !force) {
      return
    }
    $reset()

    projectUuid.value = projectUuid$

    if (projectUuid$ === undefined) {
      return
    }

    await loadProject()
  }

  /*
   * Load the current user and global settings.
   */
  const loadProject = async () => {
    // Guard against missing initialization.
    if (projectUuid.value === undefined) {
      throw new Error('projectUuid is undefined')
    }

    const response = await projectApiRetrieveRetrieve({
      client,
      path: { project: projectUuid.value },
    })
    if (response.data) {
      project.value = response.data
    }
  }

  /** Reset all attributes. */
  const $reset = () => {
    projectUuid.value = undefined
    project.value = undefined
  }

  return {
    // attributes
    projectUuid,
    project,
    // methods
    initialize,
  }
})
