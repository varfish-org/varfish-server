/// Setup the Hey API client.
import { createClient } from '@hey-api/client-fetch'

export const client = createClient({
  baseUrl: '/',
})
