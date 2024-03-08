/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution')

module.exports = {
  plugins: ['simple-import-sort', 'eslint-plugin-vue'],
  rules: {
    'comma-dangle': 0,
    'simple-import-sort/imports': 'error',
    'simple-import-sort/exports': 'error',
    'no-unused-vars': [
      'error',
      {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
      },
    ],
  },
  ignorePatterns: [
    'static/**',
    "**/node_modules/**",
    "**/svs/**", // TODO: temporary
    "**/QueryPresets/**", // TODO: temporary
    "**/QueryPresets/**", // TODO: temporary
    "**/FilterForm/**",  // TODO: temporary
  ],
  extends: [
    '@vue/typescript/recommended',
    'plugin:vue/vue3-recommended',
    '@vue/eslint-config-typescript',
    '@vue/eslint-config-prettier/skip-formatting',
    'plugin:storybook/recommended'
  ],
  root: true,
  env: {
    node: true,
    jquery: true,
  },
  rules: {
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/ban-ts-comment': 'off',
    'no-unused-vars': 'off',
    'vue/multi-word-component-names': 'off',
    'vue/require-v-for-key': 'off', // TODO: temporary
    'vue/require-default-prop': 'off', // TODO: temporary
    '@typescript-eslint/no-unused-vars': [
      'warn', // or "error"
      {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        caughtErrorsIgnorePattern: '^_'
      }
    ]
  },
  overrides: [
    {
      files: ['*.mdx'],
      extends: 'plugin:mdx/recommended'
    }
  ],
  parserOptions: {
    ecmaVersion: 'latest'
  }
}
