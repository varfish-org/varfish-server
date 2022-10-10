import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'

const app = createApp(App)

import { displayName } from '@variants/helpers'
// https://gist.github.com/sebleier/554280
import { stopWords } from '@variants/stopWords.json'

app.config.globalProperties.$filters = {
  displayName,
  displaySexIcon(sex) {
    if (sex === 2) {
      return 'fa-solid:venus'
    } else if (sex === 1) {
      return 'fa-solid:mars'
    }
    return 'fa-solid:question'
  },
  displayAffectedIcon(affected) {
    if (affected === 2) {
      return 'fa-solid:check'
    } else if (affected === 1) {
      return 'fa-solid:times'
    }
    return 'fa-solid:question'
  },
  displayAffectedColor(affected) {
    if (affected === 2) {
      return 'text-danger'
    }
    return 'text-dark'
  },
  getPubmedLinkout(symbol, hpoterms) {
    let terms = []
    for (const [_, text] of Object.entries(hpoterms)) {
      const tokens = text.toLowerCase().split(/\W+/)
      let words = []
      for (const token of tokens) {
        if (!stopWords.contains(token)) {
          words.push(token)
        }
      }
      terms.push(words.join(' AND '))
    }
    return symbol + ' AND (' + terms.join(' OR ') + ')'
  },
}

app.use(createPinia()).mount('#app')
