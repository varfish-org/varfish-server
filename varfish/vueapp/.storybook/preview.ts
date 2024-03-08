import { type Preview, setup } from '@storybook/vue3'
import { createPinia } from 'pinia'
import { type App } from 'vue'

import { registerPlugins } from './plugins'
import { withVuetifyTheme } from './withVuetifyTheme.decorator'

export const pinia = createPinia()

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: '^on[A-Z].*' },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i
      }
    },
    options: {
      // The `a` and `b` arguments in this function have a type of `import('@storybook/types').IndexEntry`. Remember that the function is executed in a JavaScript environment, so use JSDoc for IntelliSense to introspect it.
      storySort: (a /*: StoryIdentifier*/, b /*: StoryIdentifier*/) => {
        if (a.id === b.id) {
          return 0
        } else {
          return a.id.localeCompare(b.id, undefined, { numeric: true })
        }
      }
    }
  }
}

setup((app: App) => {
  // Use pinia for state management, also in pinia.
  app.use(pinia)
  // Registers your app's plugins into Storybook
  registerPlugins(app)
})

export default preview

export const decorators = [withVuetifyTheme]

export const globalTypes = {
  theme: {
    name: 'Theme',
    description: 'Global theme for components',
    toolbar: {
      icon: 'paintbrush',
      // Array of plain string values or MenuItem shape
      items: [
        { value: 'customLightTheme', title: 'Light', left: '🌞' },
        { value: 'dark', title: 'Dark', left: '🌛' }
      ],
      // Change title based on selected value
      dynamicTitle: true
    }
  }
}
