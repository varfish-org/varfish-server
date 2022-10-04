import { beforeEach, describe, expect, test } from 'vitest'

import { extractVariantZygosity } from '@/stores/clinvar-export'

describe('helper functions', () => {
  const termsRecessive = Object.freeze([
    { term_id: 'HP:0000007', term_name: 'Autosomal recessive inheritance' },
  ])
  let individuals

  beforeEach(() => {
    // Individuals
    individuals = {
      'singleton-index-uuid': {
        sodar_uuid: 'singleton-index-uuid',
        name: 'singleton-index',
        phenotype_terms: [],
        sex: 'female',
      },
      'trio-index-uuid': {
        sodar_uuid: 'trio-index-uuid',
        name: 'trio-index',
        phenotype_terms: [],
        sex: 'female',
      },
      'trio-father-uuid': {
        sodar_uuid: 'trio-father-uuid',
        name: 'trio-father',
        phenotype_terms: [],
        sex: 'male',
      },
      'trio-mother-uuid': {
        sodar_uuid: 'trio-mother-uuid',
        name: 'trio-mother',
        phenotype_terms: [],
        sex: 'female',
      },
    }
  })

  const genotypes = ['0/1', '1/0', '1/1', '0|1', '1/0', '1|1', '1']
  const sexes = ['male', 'female']
  let testTable = []
  for (const gt of genotypes) {
    for (const sex of sexes) {
      for (const recessive of [true, false]) {
        const variantAlleles = gt.match(/1/g).length
        let zygosity
        if (variantAlleles === 1) {
          if (recessive) {
            zygosity = 'Compound heterozygote'
          } else {
            zygosity = 'Single heterozygote'
          }
        } else {
          zygosity = 'Homozygote'
        }
        testTable.push(['chr11', sex, gt, zygosity, variantAlleles, recessive])
      }
    }
  }
  testTable = testTable.concat(
    ['0/1', '1/0', '1/1', '0|1', '1/0', '1|1', '1'].map((gt) => [
      'chrX',
      'male',
      gt,
      'Hemizygote',
      1,
      false,
    ]),
    ['0/1', '1/0', '1/1', '0|1', '1/0', '1|1', '1'].map((gt) => [
      'chrX',
      'female',
      gt,
      gt.match(/1/g).length === 1 ? 'Single heterozygote' : 'Homozygote',
      gt.match(/1/g).length,
      false,
    ]),
    ['0/1', '1/0', '1/1', '0|1', '1/0', '1|1', '1'].map((gt) => [
      'chrX',
      'male',
      gt,
      'Hemizygote',
      1,
      true,
    ]),
    ['0/1', '1/0', '1/1', '0|1', '1/0', '1|1', '1'].map((gt) => [
      'chrX',
      'female',
      gt,
      gt.match(/1/g).length === 1 ? 'Compound heterozygote' : 'Homozygote',
      gt.match(/1/g).length,
      true,
    ]),
    ['0/1', '1/0', '1/1', '0|1', '1/0', '1|1', '1'].map((gt) => [
      'chrY',
      'male',
      gt,
      'Hemizygote',
      1,
      false,
    ]),
    ['0/1', '1/0', '1/1', '0|1', '1/0', '1|1', '1'].map((gt) => [
      'chrY',
      'female',
      gt,
      'not provided',
      0,
      false,
    ]),
    ['0/1', '1/0', '1/1', '0|1', '1/0', '1|1', '1'].map((gt) => [
      'chrY',
      'male',
      gt,
      'Hemizygote',
      1,
      true,
    ]),
    ['0/1', '1/0', '1/1', '0|1', '1/0', '1|1', '1'].map((gt) => [
      'chrY',
      'female',
      gt,
      'not provided',
      0,
      true,
    ])
  )

  test.each(testTable)(
    'extractVariantZygosity on %s with %s singleton gt=%s expecting %s zygosity with %s variant alleles, recessive=%s',
    (chromosome, sex, gt, variantZygosity, variantAlleleCount, recessive) => {
      const smallVariant = {
        chromosome,
        genotype: {
          'singleton-index': {
            gt,
          },
        },
      }
      individuals['singleton-index-uuid'].sex = sex
      if (recessive) {
        individuals['singleton-index-uuid'].phenotype_terms = termsRecessive
      }
      const actual = extractVariantZygosity(
        smallVariant,
        ['singleton-index-uuid'],
        individuals
      )
      expect(actual).toStrictEqual({
        variantAlleleCount,
        variantZygosity,
      })
    }
  )
})
