import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  client: '@hey-api/client-fetch',
  input: '../backend/varfish/tests/drf_openapi_schema/varfish_api_schema.yaml',
  output: 'ext/varfish-api/src/lib',
  services: {
    asClass: true,
  },
});
