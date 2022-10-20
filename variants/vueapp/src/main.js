import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'

const app = createApp(App)

import { displayName } from '@varfish/helpers.js'
// https://gist.github.com/sebleier/554280
import { stopWords } from '@variants/stopWords.json'

app.config.globalProperties.$filters = {
  displayName,
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
