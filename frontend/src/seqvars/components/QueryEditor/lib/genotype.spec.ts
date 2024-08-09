import { describe, expect, test } from 'vitest'
import {
  computeFounderPathLengths,
  pickIndexFromPedigree,
  presetChoiceToGenotypeChoice,
} from './genotypes'
import { Individual, PedigreeObj } from '@/cases/stores/caseDetails'
import {
  SeqvarsGenotypeChoice,
  SeqvarsGenotypePresetChoice,
} from '@varfish-org/varfish-api/lib'

// Helper to make pedigres of various shapes.
const makePedigree = (options: {
  memberCount?: number
  affectedIndex?: boolean
  skipParentsFor?: string[]
  memberNames?: string[]
  memberSex?: (name: string) => Individual['sex']
  defaultSex?: Individual['sex']
  parentsFor?: (name: string) => { father: string; mother: string }
}) => {
  const memberCount = options.memberCount ?? 3
  const memberNames = options.memberNames ?? [
    'son',
    'father',
    'mother',
    'daughter',
  ]
  const affectedIndex = options.affectedIndex ?? true
  const skipParentsFor = options.skipParentsFor ?? ['father', 'mother']
  const memberSex =
    options.memberSex ??
    ((name: string) => {
      switch (name) {
        case 'index':
        case 'son':
        case 'father':
          return 'male'
        case 'daugther':
        case 'mother':
          return 'female'
        default:
          return defaultSex
      }
    })
  const defaultSex = options.defaultSex ?? 'male'
  const parentsFor =
    options.parentsFor ??
    ((name: string) => {
      if (skipParentsFor.includes(name)) {
        return { father: '0', mother: '0' }
      }
      const usedMembers = memberNames.slice(0, memberCount)
      const father = !!usedMembers.find((name) => name === 'father')
        ? 'father'
        : '0'
      const mother = !!usedMembers.find((name) => name === 'mother')
        ? 'mother'
        : '0'
      switch (name) {
        case 'son':
        case 'daughter':
          return { father, mother }
        default:
          return { father: '0', mother: '0' }
      }
    })

  if (memberCount > memberNames.length) {
    throw new Error('Not enough member names')
  }

  const result: PedigreeObj = {
    individual_set: [],
    // below unused in test
    sodar_uuid: 'sodar_uuid',
    case: 'case',
    date_created: 'date_created',
    date_modified: 'date_modified',
  }

  for (let i = 0; i < memberCount; i++) {
    const memberName = memberNames[i]
    const member: Individual = {
      name: memberName,
      affected: i === 0 && affectedIndex,
      sex: memberSex(memberName),
      ...parentsFor(memberName),
      // below unused in test
      sodar_uuid: 'sodar_uuid',
      pedigree: 'pedigree',
      date_created: 'date_created',
      date_modified: 'date_modified',
      assay: 'wgs' as Individual['assay'],
      karyotypic_sex: 'unknown' as Individual['karyotypic_sex'],
    }
    if (i > 0 && !skipParentsFor.includes(memberName)) {
      member.father = 'father'
      member.mother = 'mother'
    }
    result.individual_set.push(member)
  }

  return result
}

describe('computeFounderPathLengths', () => {
  test('singleton with affected index', {}, () => {
    const result = computeFounderPathLengths(
      makePedigree({ memberCount: 1, affectedIndex: true }),
    )
    expect(result).toEqual(new Map([['son', 0]]))
  })

  test('singleton with unaffected index', {}, () => {
    const result = computeFounderPathLengths(
      makePedigree({ memberCount: 1, affectedIndex: false }),
    )
    expect(result).toEqual(new Map([['son', 0]]))
  })

  test('trio with affected index', {}, () => {
    const result = computeFounderPathLengths(
      makePedigree({ memberCount: 3, affectedIndex: true }),
    )
    expect(result).toEqual(
      new Map([
        ['son', 1],
        ['father', 0],
        ['mother', 0],
      ]),
    )
  })

  test('trio with unaffected index', {}, () => {
    const result = computeFounderPathLengths(
      makePedigree({ memberCount: 3, affectedIndex: false }),
    )
    expect(result).toEqual(
      new Map([
        ['son', 1],
        ['father', 0],
        ['mother', 0],
      ]),
    )
  })

  test('quatro with affected index', {}, () => {
    const result = computeFounderPathLengths(
      makePedigree({ memberCount: 4, affectedIndex: true }),
    )
    expect(result).toEqual(
      new Map([
        ['son', 1],
        ['father', 0],
        ['mother', 0],
        ['daughter', 1],
      ]),
    )
  })

  test('trio with unaffected index', {}, () => {
    const result = computeFounderPathLengths(
      makePedigree({ memberCount: 4, affectedIndex: false }),
    )
    expect(result).toEqual(
      new Map([
        ['son', 1],
        ['father', 0],
        ['mother', 0],
        ['daughter', 1],
      ]),
    )
  })
})

describe('pickIndexFromPedigree', () => {
  test('singleton with affected index', {}, () => {
    const result = pickIndexFromPedigree(
      makePedigree({ memberCount: 1, affectedIndex: true }),
    )
    expect(result).toBe('son')
  })

  test('singleton with unaffected index', {}, () => {
    const result = pickIndexFromPedigree(
      makePedigree({ memberCount: 1, affectedIndex: false }),
    )
    expect(result).toBe('son')
  })

  test('trio with affected index', {}, () => {
    const result = pickIndexFromPedigree(
      makePedigree({ memberCount: 3, affectedIndex: true }),
    )
    expect(result).toBe('son')
  })

  test('trio with unaffected index', {}, () => {
    const result = pickIndexFromPedigree(
      makePedigree({ memberCount: 3, affectedIndex: false }),
    )
    expect(result).toBe('son')
  })

  test('quatro with affected index', {}, () => {
    const result = pickIndexFromPedigree(
      makePedigree({ memberCount: 4, affectedIndex: true }),
    )
    expect(result).toBe('son')
  })

  test('quatro with unaffected index', {}, () => {
    const result = pickIndexFromPedigree(
      makePedigree({ memberCount: 4, affectedIndex: false }),
    )
    expect(result).toBe('son')
  })
})

describe('presetChoiceToGenotypeChoice', () => {
  test.each([
    ['any', ['any']],
    ['de_novo', ['variant']],
    ['dominant', ['het']],
    ['homozygous_recessive', ['recessive_index']],
    ['compound_heterozygous_recessive', ['recessive_index']],
    ['recessive', ['recessive_index']],
    ['x_recessive', ['recessive_index']],
    ['affected_carriers', ['variant']],
  ] as [SeqvarsGenotypePresetChoice, SeqvarsGenotypeChoice[]][])(
    'presetChoiceToGenotypeChoice(<singleton with affected index>, %s) -> %s',
    (
      choice: SeqvarsGenotypePresetChoice,
      expected: SeqvarsGenotypeChoice[],
    ) => {
      const pedigree = makePedigree({ memberCount: 1, affectedIndex: true })
      const result = presetChoiceToGenotypeChoice(pedigree, choice)
      const expectedFull = expected.map((genotype, i) => ({
        sample: pedigree.individual_set[i].name,
        genotype,
        enabled: true,
        include_no_call: false,
      }))
      expect(result).toStrictEqual(expectedFull)
    },
  )

  test.each([
    ['any', ['any']],
    ['de_novo', ['variant']],
    ['dominant', ['ref']],
    ['homozygous_recessive', ['recessive_index']],
    ['compound_heterozygous_recessive', ['recessive_index']],
    ['recessive', ['recessive_index']],
    ['x_recessive', ['recessive_index']],
    ['affected_carriers', ['ref']],
  ] as [SeqvarsGenotypePresetChoice, SeqvarsGenotypeChoice[]][])(
    'presetChoiceToGenotypeChoice(<singleton with unaffected index>, %s) -> %s',
    (
      choice: SeqvarsGenotypePresetChoice,
      expected: SeqvarsGenotypeChoice[],
    ) => {
      const pedigree = makePedigree({ memberCount: 1, affectedIndex: false })
      const result = presetChoiceToGenotypeChoice(pedigree, choice)
      const expectedFull = expected.map((genotype, i) => ({
        sample: pedigree.individual_set[i].name,
        genotype,
        enabled: true,
        include_no_call: false,
      }))
      expect(result).toStrictEqual(expectedFull)
    },
  )

  test.each([
    ['any', ['any', 'any', 'any']],
    ['de_novo', ['variant', 'ref', 'ref']],
    ['dominant', ['het', 'ref', 'ref']],
    [
      'homozygous_recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother'],
    ],
    [
      'compound_heterozygous_recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother'],
    ],
    ['recessive', ['recessive_index', 'recessive_father', 'recessive_mother']],
    [
      'x_recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother'],
    ],
    ['affected_carriers', ['variant', 'ref', 'ref']],
  ] as [SeqvarsGenotypePresetChoice, SeqvarsGenotypeChoice[]][])(
    'presetChoiceToGenotypeChoice(<trio with affected index>, %s) -> %s',
    (
      choice: SeqvarsGenotypePresetChoice,
      expected: SeqvarsGenotypeChoice[],
    ) => {
      const pedigree = makePedigree({ memberCount: 3, affectedIndex: true })
      const result = presetChoiceToGenotypeChoice(pedigree, choice)
      const expectedFull = expected.map((genotype, i) => ({
        sample: pedigree.individual_set[i].name,
        genotype,
        enabled: true,
        include_no_call: false,
      }))
      expect(result).toStrictEqual(expectedFull)
    },
  )

  test.each([
    ['any', ['any', 'any', 'any']],
    ['de_novo', ['variant', 'ref', 'ref']],
    ['dominant', ['ref', 'ref', 'ref']],
    [
      'homozygous_recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother'],
    ],
    [
      'compound_heterozygous_recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother'],
    ],
    ['recessive', ['recessive_index', 'recessive_father', 'recessive_mother']],
    [
      'x_recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother'],
    ],
    ['affected_carriers', ['ref', 'ref', 'ref']],
  ] as [SeqvarsGenotypePresetChoice, SeqvarsGenotypeChoice[]][])(
    'presetChoiceToGenotypeChoice(<trio with unaffected index>, %s) -> %s',
    (
      choice: SeqvarsGenotypePresetChoice,
      expected: SeqvarsGenotypeChoice[],
    ) => {
      const pedigree = makePedigree({ memberCount: 3, affectedIndex: false })
      const result = presetChoiceToGenotypeChoice(pedigree, choice)
      const expectedFull = expected.map((genotype, i) => ({
        sample: pedigree.individual_set[i].name,
        genotype,
        enabled: true,
        include_no_call: false,
      }))
      expect(result).toStrictEqual(expectedFull)
    },
  )

  test.each([
    ['any', ['any', 'any', 'any', 'any']],
    ['de_novo', ['variant', 'ref', 'ref', 'ref']],
    ['dominant', ['het', 'ref', 'ref', 'ref']],
    [
      'homozygous_recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother', 'any'],
    ],
    [
      'compound_heterozygous_recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother', 'any'],
    ],
    [
      'recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother', 'any'],
    ],
    [
      'x_recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother', 'any'],
    ],
    ['affected_carriers', ['variant', 'ref', 'ref', 'ref']],
  ] as [SeqvarsGenotypePresetChoice, SeqvarsGenotypeChoice[]][])(
    'presetChoiceToGenotypeChoice(<quatro with affected index>, %s) -> %s',
    (
      choice: SeqvarsGenotypePresetChoice,
      expected: SeqvarsGenotypeChoice[],
    ) => {
      const pedigree = makePedigree({ memberCount: 4, affectedIndex: true })
      const result = presetChoiceToGenotypeChoice(pedigree, choice)
      const expectedFull = expected.map((genotype, i) => ({
        sample: pedigree.individual_set[i].name,
        genotype,
        enabled: true,
        include_no_call: false,
      }))
      expect(result).toStrictEqual(expectedFull)
    },
  )

  test.each([
    ['any', ['any', 'any', 'any', 'any']],
    ['de_novo', ['variant', 'ref', 'ref', 'ref']],
    ['dominant', ['ref', 'ref', 'ref', 'ref']],
    [
      'homozygous_recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother', 'any'],
    ],
    [
      'compound_heterozygous_recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother', 'any'],
    ],
    [
      'recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother', 'any'],
    ],
    [
      'x_recessive',
      ['recessive_index', 'recessive_father', 'recessive_mother', 'any'],
    ],
    ['affected_carriers', ['ref', 'ref', 'ref', 'ref']],
  ] as [SeqvarsGenotypePresetChoice, SeqvarsGenotypeChoice[]][])(
    'presetChoiceToGenotypeChoice(<quatro with unaffected index>, %s) -> %s',
    (
      choice: SeqvarsGenotypePresetChoice,
      expected: SeqvarsGenotypeChoice[],
    ) => {
      const pedigree = makePedigree({ memberCount: 4, affectedIndex: false })
      const result = presetChoiceToGenotypeChoice(pedigree, choice)
      const expectedFull = expected.map((genotype, i) => ({
        sample: pedigree.individual_set[i].name,
        genotype,
        enabled: true,
        include_no_call: false,
      }))
      expect(result).toStrictEqual(expectedFull)
    },
  )
})
