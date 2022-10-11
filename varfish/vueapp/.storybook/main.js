const { mergeConfig } = require('vite')
const Components = require('unplugin-vue-components/vite')
const IconsResolver = require('unplugin-icons/resolver')
const Icons = require('unplugin-icons/vite')
const { resolve } = require('path')

module.exports = {
  async viteFinal(config, { configType }) {
    return mergeConfig(config, {
      plugins: [
        Components({
          resolvers: [IconsResolver()],
        }),
        Icons({
          autoInstall: true,
          compiler: 'vue3',
        }),
      ],
      resolve: {
        alias: {
          '@clinvarexport': resolve(__dirname, '../src/clinvarexport'),
          '@clinvarexportTest': resolve(__dirname, '../tests/clinvarexport'),
          '@variants': resolve(__dirname, '../src/variants'),
          '@variantsTest': resolve(__dirname, '../tests/variants'),
        },
        preserveSymlinks: true,
      },
    })
  },
  stories: ['../src/**/*.stories.mdx', '../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
  ],
  framework: '@storybook/vue3',
  core: {
    builder: '@storybook/builder-vite',
  },
  features: {
    storyStoreV7: true,
  },
}
