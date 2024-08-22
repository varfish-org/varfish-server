import { describe, expect, it } from 'vitest'

import { deepCopyAndOmit } from './copy'

describe('deepCopyAndOmit', () => {
  it('should deeply copy an object and omit specified keys', () => {
    const original = {
      name: 'John',
      age: 30,
      password: 'secret',
      nested: {
        token: 'abc123',
        details: {
          email: 'john@example.com',
        },
      },
    }

    const keysToOmit = ['password', 'token']
    const copied = deepCopyAndOmit(original, keysToOmit)

    expect(copied).toEqual({
      name: 'John',
      age: 30,
      nested: {
        details: {
          email: 'john@example.com',
        },
      },
    })

    // Ensure original object is not modified
    expect(original).toEqual({
      name: 'John',
      age: 30,
      password: 'secret',
      nested: {
        token: 'abc123',
        details: {
          email: 'john@example.com',
        },
      },
    })
  })

  it('should deeply copy arrays and omit keys within objects in the arrays', () => {
    const original = {
      users: [
        { name: 'Alice', password: '123' },
        { name: 'Bob', password: '456' },
      ],
      settings: {
        theme: 'dark',
        secret: 'xyz',
      },
    }

    const keysToOmit = ['password', 'secret']
    const copied = deepCopyAndOmit(original, keysToOmit)

    expect(copied).toEqual({
      users: [{ name: 'Alice' }, { name: 'Bob' }],
      settings: {
        theme: 'dark',
      },
    })
  })

  it('should handle non-object values correctly', () => {
    const original = 42 // Primitive value
    const copied = deepCopyAndOmit(original, [])

    expect(copied).toBe(42) // Should be the same primitive value
  })

  it('should handle empty objects and arrays', () => {
    const original = {
      emptyArray: [],
      emptyObject: {},
    }

    const copied = deepCopyAndOmit(original, ['unusedKey'])

    expect(copied).toEqual({
      emptyArray: [],
      emptyObject: {},
    })
  })

  it('should return an empty object if all keys are omitted', () => {
    const original = {
      name: 'John',
      age: 30,
      password: 'secret',
    }

    const keysToOmit = ['name', 'age', 'password']
    const copied = deepCopyAndOmit(original, keysToOmit)

    expect(copied).toEqual({})
  })

  it('should work with nested arrays and objects', () => {
    const original = {
      level1: {
        level2: [
          { key1: 'value1', key2: 'value2' },
          { key3: 'value3', key4: 'value4' },
        ],
        level2Object: {
          key5: 'value5',
          key6: 'value6',
        },
      },
    }

    const keysToOmit = ['key2', 'key4', 'key6']
    const copied = deepCopyAndOmit(original, keysToOmit)

    expect(copied).toEqual({
      level1: {
        level2: [{ key1: 'value1' }, { key3: 'value3' }],
        level2Object: {
          key5: 'value5',
        },
      },
    })
  })

  it('should handle cases where no keys are omitted', () => {
    const original = {
      name: 'John',
      age: 30,
    }

    const keysToOmit: string[] = []
    const copied = deepCopyAndOmit(original, keysToOmit)

    expect(copied).toEqual(original)
    expect(copied).not.toBe(original) // Ensure deep copy
  })
})
