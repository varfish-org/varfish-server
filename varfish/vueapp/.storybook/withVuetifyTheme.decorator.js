import { h } from 'vue'

import StoryWrapper from './StoryWrapper.vue'

export const DEFAULT_THEME = 'customLightTheme'

export const withVuetifyTheme = (storyFn, context) => {
  // Pull our global theme variable, fallback to DEFAULT_THEME
  const themeName = context.globals.theme || DEFAULT_THEME
  const story = storyFn()

  return () => {
    return h(
      StoryWrapper,
      { themeName },
      {
        story: () => h(story, { ...context.args })
      }
    )
  }
}
