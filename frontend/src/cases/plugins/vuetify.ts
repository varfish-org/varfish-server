/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */
// Styles
import '@mdi/font/css/materialdesignicons.css'
// Composables
import { VSnackbarQueue } from 'vuetify/labs/VSnackbarQueue'
import { type ThemeDefinition, createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import { md3 } from 'vuetify/blueprints'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '../styles/main.scss'

const customLightTheme: ThemeDefinition = {
  dark: false,
  colors: {
    'surface-variant': '#333F50',
    'on-surface-variant': '#FFFFFF',
    primary: '#333F50',
    secondary: '#3f50b5',
    tertiary: '#002884',
    background: '#eeeeee',
    success: '#4caf50',
    warning: '#ff9800',
    error: '#f44336',
    info: '#f0f2f5',

    'hint-text': '#757575',
    'ui-aux-text': '#595959',
    'ui-control-text': '#242424',
    'ui-control-text-disabled': '#BDBDBD',
    'inactive-ui-element': '#D7D7D7',

    bg: '#FFFFFF',
    'hover-bg': '#FAFAFA',
    'selected-bg': '#F3F9FF',
    'bg-alt': '#F9F9F9',

    'modification-indicator': '#DC9E00',
    rating5: '#A21C19',
    rating4: '#DC9E00',
    rating3: '#DC9E00',
    ratingX: '#DC9E00',
  },
}

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export const vuetify = createVuetify({
  blueprint: md3,
  components: {
    VSnackbarQueue, // labs; needs to be explicitly added
    ...components,
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  directives,
  defaults: {
    global: {
      flat: true,
    },
    VCard: {
      rounded: 'lg',
    },
    VSheet: {
      rounded: 'lg',
    },
    VChip: {
      rounded: 'xl',
    },
  },
  theme: {
    defaultTheme: 'customLightTheme',
    themes: {
      customLightTheme,
    },
  },
})
