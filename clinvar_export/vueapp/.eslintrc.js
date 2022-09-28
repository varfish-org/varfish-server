module.exports = {
  plugins: ['simple-import-sort'],
  rules: {
    'comma-dangle': 0,
    'simple-import-sort/imports': 'error',
    'simple-import-sort/exports': 'error',
  },
  extends: ['plugin:vue/recommended', '@vue/standard', 'prettier'],
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
