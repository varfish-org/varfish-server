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
  checkIsVariantMtHomopolymer(smallVariant) {
    const positionCheck = (pos) => {
      return (
        (pos >= 66 && pos <= 71) ||
        (pos >= 300 && pos <= 316) ||
        (pos >= 513 && pos <= 525) ||
        (pos >= 3106 && pos <= 3107) ||
        (pos >= 12418 && pos <= 12425) ||
        (pos >= 16182 && pos <= 16194)
      )
    }
    if (smallVariant.chromosome === 'MT') {
      return (
        positionCheck(smallVariant.start) || positionCheck(smallVariant.end)
      )
    }
  },
  displayAmbiguousFrequencyWarning(item) {
    const tables = [
      'exac',
      'thousand_genomes',
      'gnomad_exomes',
      'gnomad_genomes',
      'inhouse',
    ]
    let ambiguousTables = []
    for (const table of tables) {
      const hom_field =
        table === 'inhouse' ? 'inhouse_hom_alt' : table + '_homozygous'
      if (
        item[hom_field] > 50 ||
        (table !== 'inhouse' && item[table + '_frequency'] > 0.1)
      ) {
        ambiguousTables.push(table)
      }
    }
    return ambiguousTables
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
  displayFlagColor(value) {
    if (value === 'positive') {
      return 'text-danger'
    } else if (value === 'uncertain') {
      return 'text-warning'
    } else if (value === 'negative') {
      return 'text-success'
    } else if (value === 'empty') {
      return 'text-secondary'
    } else {
      return ''
    }
  },
  displayFlagIcon(value) {
    if (value === 'positive') {
      return 'fa-solid:exclamation-circle'
    } else if (value === 'uncertain') {
      return 'fa-solid:question'
    } else if (value === 'negative') {
      return 'fa-solid:minus-circle'
    } else if (value === 'empty') {
      return 'fa-solid:times'
    }
  },
  displayMutedIfFalse(condition) {
    if (!condition) {
      return 'text-muted'
    }
    return 'text-dark'
  },
  displayOpacityIfFalse(condition) {
    if (!condition) {
      return 'opacity: 20%'
    }
    return ''
  },
}

app.use(createPinia()).mount('#app')
