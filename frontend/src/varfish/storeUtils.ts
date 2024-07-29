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
  state: State = State.Initial
  /** Message to display for store state, e.g., in overlay. */
  message: string | null = null
  /** How many server interactions are running */
  serverInteractions: number = 0

  /**
   * Reset the store state.
   */
  reset(): void {
    this.state = State.Initial
    this.message = null
    this.serverInteractions = 0
  }

  /**
   * Helper function to implement RAAI-like execution of queries, excuting state and server
   * interactions accordingly.
   *
   * @param asyncCallable The async function to execute.
   * @param transformError Optional function to transform error messages.
   * @returns The result of the async function.
   * @throws The error of the async function.
   */
  async execAsync<T, E>(
    asyncCallable: () => Promise<T>,
    transformError?: (e: E) => string,
  ): Promise<T> {
    this.state = State.Fetching
    this.serverInteractions += 1
    try {
      const result = await asyncCallable()
      this.state = State.Active
      return result
    } catch (error) {
      this.state = State.Error
      if (transformError) {
        let e = error as E
        this.message = transformError(e)
      } else {
        this.message = `Error: ${error}`
      }
      throw error
    } finally {
      this.serverInteractions -= 1
    }
  }
}
