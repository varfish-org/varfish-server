import { createRouter, createWebHistory } from 'vue-router'

import HomeStorybook from '../HomeStorybook.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeStorybook
  },
  {
    path: '/gene-details/:gene',
    name: 'gene-details',
    component: HomeStorybook
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})
