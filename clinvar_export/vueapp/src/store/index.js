import Vue from 'vue'
import Vuex, { createLogger } from 'vuex'

import clinvarExport from './modules/clinvarExport'
// import products from './modules/products'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

export default new Vuex.Store({
  modules: {
    clinvarExport,
  },
  strict: debug,
  plugins: debug ? [createLogger()] : [],
})
