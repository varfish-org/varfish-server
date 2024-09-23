import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  client: '@hey-api/client-fetch',
  input: 'ext/viguno-api/openapi.yaml',
  output: 'ext/viguno-api/src/lib',
  plugins: [
    '@tanstack/vue-query'
  ]
});
