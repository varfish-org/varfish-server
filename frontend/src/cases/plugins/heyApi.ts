/// Setup the Hey API client.
import { createClient } from '@hey-api/client-fetch'

/** Client for the VarFish API. */
export const client = createClient({
  baseUrl: '/',
})

/** Client for the Viguno API. */
export const vigunoClient = createClient({
  baseUrl: '/proxy/varfish/viguno/',
})
