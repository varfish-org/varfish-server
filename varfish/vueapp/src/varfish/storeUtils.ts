import { ref } from 'vue'

/**
 * The possible states of a store.
 */
export enum State {
  Initial = 'initial',
  Fetching = 'fetching',
  Active = 'active',
  Error = 'error',
}

/**
 * Encapsulate store state.
 *
 * This includes the `State` istelf, a text message, and the number of server interactions.
 */
export class StoreState {
  /** Current store's state. */
  state = ref<State>(State.Initial)
  /** Message to display for store state, e.g., in overlay. */
  message = ref<string | null>(null)
  /** How many server interactions are running */
  serverInteractions = ref<number>(0)
}
