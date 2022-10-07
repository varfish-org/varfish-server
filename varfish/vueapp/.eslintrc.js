module.exports = {
  plugins: ['simple-import-sort', 'eslint-plugin-vue'],
  rules: {
    'comma-dangle': 0,
    'simple-import-sort/imports': 'error',
    'simple-import-sort/exports': 'error',
    'no-unused-vars': [
      'error',
      { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
    ],
  },
  extends: ['eslint:recommended', 'plugin:vue/vue3-recommended', 'prettier'],
  root: true,
  env: {
    node: true,
    jquery: true,
  },
  parserOptions: {
    parser: '@babel/eslint-parser',
  },
  overrides: [
    {
      files: ['**/tests/unit/**/*.spec.js'],
      env: {
        jest: true,
      },
    },
  ],
}
