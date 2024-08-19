import { PedigreeObj } from '@/cases/stores/caseDetails'
import {
  SeqvarsGenotypePresetChoice,
  SeqvarsSampleGenotypePydantic,
} from '@varfish-org/varfish-api/lib'

/**
 * Compute the longest path from a member to a founder in the pedigree.
 *
 * @param pedigree The `PedigreeObj` to use for family members.
 * @returns A map from member name to longest path to a founder.
 */
export const computeFounderPathLengths = (
  pedigree: PedigreeObj,
): Map<string, number> => {
  const result = new Map<string, number>()
  const memberNames = new Set<string>(
    pedigree.individual_set.map((member) => member.name),
  )

  // Detect the case where we would make no progress - father/mother set but
  // unknown.
  for (const memberObj of pedigree.individual_set) {
    if (
      !!memberObj.father &&
      memberObj.father !== '0' &&
      !memberNames.has(memberObj.father) &&
      !!memberObj.mother &&
      memberObj.mother !== '0' &&
      !memberNames.has(memberObj.mother)
    ) {
      throw new Error(
        `Could not find father ${memberObj.father} or mother ${memberObj.mother} for member ${memberObj.name}`,
      )
    }
  }

  // Process all pedigree members, building a map of member name to longest path.
  let iteration: number = 0
  const toProcess = new Set<string>(memberNames)
  while (result.size < pedigree.individual_set.length) {
    iteration += 1
    if (iteration > pedigree.individual_set.length) {
      throw new Error('Infinite loop over pedigree members detected')
    }

    const toRemove = new Set<string>()
    for (const memberName of toProcess) {
      const memberObj = pedigree.individual_set.find(
        (m) => m.name === memberName,
      )
      if (!memberObj) {
        throw new Error(`Could not find member ${memberName}`)
      }
      if (
        (!memberObj.father || memberObj.father === '0') &&
        (!memberObj.mother || memberObj.mother === '0')
      ) {
        result.set(memberName, 0)
        toRemove.add(memberName)
      } else if (
        !!memberObj.father &&
        result.has(memberObj.father) &&
        !!memberObj.mother &&
        result.has(memberObj.mother)
      ) {
        result.set(
          memberName,
          Math.max(
            result.get(memberObj.father)!,
            result.get(memberObj.mother)!,
          ) + 1,
        )
        toRemove.add(memberName)
      }
    }
    for (const member of toRemove) {
      toProcess.delete(member)
    }
  }

  return result
}

/**
 * Pick index from the pedigree.
 *
 * The following heuristic is used. In the case of more than one match, use the first one found.
 *
 * - Compute the longest path of the individual to a founder (individual without any parents).
 * - Pick affected individual with the longest path.
 * - If there are no affected individual, pick first unaffected with the longest path.
 *
 * @param pedigree The `PedigreeObj` to use for family members.
 * @returns The index of the individual to use.
 * @throws Error if no individual can be picked (empty).
 */
export const pickIndexFromPedigree = (pedigree: PedigreeObj): string => {
  const founderPathLengths = computeFounderPathLengths(pedigree)
  if (founderPathLengths.size === 0) {
    throw new Error('No individual in pedigree')
  }

  const longestPathLength = Math.max(...Array.from(founderPathLengths.values()))
  let firstLongestFound: string | undefined = undefined
  for (const individual of pedigree.individual_set) {
    const memberName = individual.name
    const pathLength = founderPathLengths.get(memberName)!
    if (pathLength === longestPathLength) {
      if (firstLongestFound === undefined) {
        firstLongestFound = memberName
      }
      if (
        pedigree.individual_set.find((m) => m.name === memberName)?.affected
      ) {
        return memberName
      }
    }
  }

  return firstLongestFound!
}

/**
 * Compute the genotype choice (for input to query engine) from pedigree and genotype presets
 * choice.
 *
 * @param pedigree The `PedigreeObj` to use for family members.
 * @param genotypeChoice The genotype preset choice to use.
 */
export const presetChoiceToGenotypeChoice = (
  pedigree: PedigreeObj,
  genotypeChoice: SeqvarsGenotypePresetChoice,
): SeqvarsSampleGenotypePydantic[] => {
  const memberNames = pedigree.individual_set.map((m) => m.name)
  const isAffected = new Map<string, boolean>(
    pedigree.individual_set.map((m) => [m.name, m.affected]),
  )
  const indexName = pickIndexFromPedigree(pedigree)
  const index = pedigree.individual_set.find((m) => m.name === indexName)
  if (!index) {
    throw new Error('Could not find index in pedigree')
  }
  const fatherName = pedigree.individual_set.find(
    (m) => m.name === index.father,
  )?.name
  const motherName = pedigree.individual_set.find(
    (m) => m.name === index.mother,
  )?.name

  switch (genotypeChoice) {
    case 'any':
      return memberNames.map(
        (sampleName): SeqvarsSampleGenotypePydantic => ({
          sample: sampleName,
          genotype: 'any',
          enabled: true,
          include_no_call: false,
        }),
      )
    case 'de_novo':
      return memberNames.map((sampleName): SeqvarsSampleGenotypePydantic => {
        if (sampleName === indexName) {
          return {
            sample: sampleName,
            genotype: 'variant',
            enabled: true,
            include_no_call: false,
          }
        } else {
          return {
            sample: sampleName,
            genotype: 'ref',
            enabled: true,
            include_no_call: false,
          }
        }
      })
    case 'dominant':
      return memberNames.map((sampleName): SeqvarsSampleGenotypePydantic => {
        if (isAffected.get(sampleName) === true) {
          return {
            sample: sampleName,
            genotype: 'het',
            enabled: true,
            include_no_call: false,
          }
        } else {
          return {
            sample: sampleName,
            genotype: 'ref',
            enabled: true,
            include_no_call: false,
          }
        }
      })
    case 'compound_heterozygous_recessive':
    case 'recessive':
    case 'x_recessive':
    case 'homozygous_recessive':
      return memberNames.map((sampleName): SeqvarsSampleGenotypePydantic => {
        if (indexName === sampleName) {
          return {
            sample: sampleName,
            genotype: 'recessive_index',
            enabled: true,
            include_no_call: false,
          }
        } else if (!!fatherName && sampleName === fatherName) {
          return {
            sample: sampleName,
            genotype: 'recessive_father',
            enabled: true,
            include_no_call: false,
          }
        } else if (!!motherName && sampleName === motherName) {
          return {
            sample: sampleName,
            genotype: 'recessive_mother',
            enabled: true,
            include_no_call: false,
          }
        } else {
          return {
            sample: sampleName,
            genotype: 'any',
            enabled: true,
            include_no_call: false,
          }
        }
      })
    case 'affected_carriers':
      return memberNames.map((sampleName): SeqvarsSampleGenotypePydantic => {
        if (isAffected.get(sampleName) === true) {
          return {
            sample: sampleName,
            genotype: 'variant',
            enabled: true,
            include_no_call: false,
          }
        } else {
          return {
            sample: sampleName,
            genotype: 'ref',
            enabled: true,
            include_no_call: false,
          }
        }
      })
  }
}
