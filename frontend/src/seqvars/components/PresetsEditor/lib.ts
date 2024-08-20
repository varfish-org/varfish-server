import {
  GenomeRegionPydanticList,
  SeqvarsGenotypePresetChoice,
} from '@varfish-org/varfish-api/lib'
import { Ref, computed, ref } from 'vue'

import { formatLargeInt } from '@/varfish/helpers'

// Source: https://dev.to/razi91/using-v-model-with-custom-setters-4hni
export type ProxySetters<T extends object> = Partial<{
  [K in keyof T]: (target: T, value: T[K]) => Partial<T> | Promise<Partial<T>>
}>

// Source: https://dev.to/razi91/using-v-model-with-custom-setters-4hni
export function toProxy<T extends object>(opt: {
  target: Ref<T>
  setters: ProxySetters<T>
}) {
  // <(string & {})> -- a trick for "any string, but still suggest the keys"
  // eslint-disable-next-line @typescript-eslint/ban-types
  const currentlySetting = ref<keyof T | (string & {})>()

  function setFields(toSet: Partial<T>) {
    opt.target.value = {
      ...opt.target.value,
      ...toSet,
    }
  }

  const proxy = computed({
    get() {
      return new Proxy(opt.target.value, {
        get(target: T, key: string) {
          return target[key as keyof T]
        },
        set(target: T, key: string, value: any) {
          if (currentlySetting.value) return false
          const setterFn = opt.setters[key as keyof T]
          if (setterFn) {
            currentlySetting.value = key
            const toSet = setterFn(target, value)
            if (toSet instanceof Promise) {
              toSet
                .then(setFields)
                .finally(() => (currentlySetting.value = undefined))
            } else {
              setFields(toSet)
              currentlySetting.value = undefined
            }
          } else {
            opt.target.value[key as keyof T] = value
          }
          return true
        },
      })
    },
    set(v) {
      opt.target.value = v
    },
  })

  return {
    proxy,
    currentlySetting,
    isProcessing: computed(() => currentlySetting.value != undefined),
  }
}

/** Helper type to unpack, e.g., `Array<T1 | T2>`. */
type _Unpacked<T> = T extends (infer U)[] ? U : T

/** Helper type for one GenomeRegion */
export type GenomeRegion = _Unpacked<GenomeRegionPydanticList>

/**
 * Return user-readable string representation of a `GenomeRegion`.
 *
 * @param genomeRegion The `GenomeRegion` to convert to a string.
 * @returns The user-readable string representation of the `GenomeRegion`.
 */
export const genomeRegionToString = (genomeRegion: GenomeRegion): string => {
  const chromStr = genomeRegion.chromosome.startsWith('chr')
    ? genomeRegion.chromosome
    : `chr${genomeRegion.chromosome}`
  if (genomeRegion.range) {
    const start = formatLargeInt(genomeRegion.range.start)
    const end = formatLargeInt(genomeRegion.range.end)
    return `${chromStr}:${start}-${end}`
  } else {
    return chromStr
  }
}

/** Regular expression for chromosome (1, 22, X, Y, M/MT) */
const CHROMOSOME_RE = /^(chr)?([1-9]|1[0-9]|2[0-2]|x|y|m|mt)$/

/**
 * Attempt to parse `GenomeRegion` from text.
 *
 * @param text The text to parse.
 * @returns The parsed `GenomeRegion`.
 * @throws Error if the input is invalid.
 */
export const parseGenomeRegion = (text: string): GenomeRegion => {
  // Guard against multiple colons.
  if ((text.match(/:/g) || []).length > 1) {
    throw new Error('Too many colons in input')
  }

  // Otherwise, split by colon.
  const parts = text.split(':')

  // Now, validate chromosome, strip 'chr' prefix, and normalize 'MT'
  // to 'M' necessary.
  let chromosome = parts[0].toLowerCase()
  // Check that chromosome is valid.
  if (!chromosome.match(CHROMOSOME_RE)) {
    throw new Error(`Invalid chromosome: ${chromosome}`)
  }
  // Remove "chr" prefix if present.
  if (chromosome.startsWith('chr')) {
    chromosome = chromosome.slice(3)
  }
  // Normalize "MT" to "M".
  if (chromosome === 'mt') {
    chromosome = 'm'
  }
  chromosome = chromosome.toUpperCase()
  // If we only have the chromosome, we are done.
  if (parts.length === 1) {
    return { chromosome }
  }

  // Parse out the range.
  let range = parts[1]
  if ((range.match(/-/g) || []).length > 1) {
    throw new Error('Invalid range: too many hyphens')
  }
  // Strip any commas.
  range = range.replace(/,/g, '')
  // Split by hyphen and convert to number.
  const rangeArr = range.split('-').map((x) => parseInt(x, 10))
  const [start, end] = rangeArr
  // Check whether conversion was successful.
  if (isNaN(start) || isNaN(end)) {
    throw new Error('Invalid range: NaN found')
  }
  // Check that start is not greater than end.
  if (start > end) {
    throw new Error('Invalid range: start greater than end')
  }
  // Otherwise, we are good.
  return { chromosome, range: { start, end } }
}

/** Labels for genotype presets. */
export const GENOTYPE_PRESET_LABELS: {
  [key in SeqvarsGenotypePresetChoice]: string
} = {
  any: 'Any',
  de_novo: 'De novo',
  dominant: 'Dominant',
  homozygous_recessive: 'Homozygous recessive',
  compound_heterozygous_recessive: 'Compound heterozygous recessive',
  recessive: 'Recessive',
  x_recessive: 'X-linked recessive',
  affected_carriers: 'Affected carriers',
}

/** Debounce wait value for category presets updates. */
export const CATEGORY_PRESETS_DEBOUNCE_WAIT = 500

/** Enumeration for the presets categories. */
export enum PresetsCategory {
  QUALITY = 'quality',
  FREQUENCY = 'frequency',
  CONSEQUENCE = 'consequence',
  LOCUS = 'locus',
  PHENOTYPE_PRIO = 'phenotype_prioritization',
  VARIANT_PRIO = 'variant_prioritization',
  CLINVAR = 'clinvar',
  COLUMNS = 'columns',
  PREDEFINED_QUERIES = 'predefined_queries',
}

/** Type for the category items. */
export interface PresetsListItem {
  sodar_uuid: string
  label: string
  rank?: number
}

/** Information about one category. */
export interface PresetsCategoryInfo {
  label: string
  category: PresetsCategory
  items: PresetsListItem[]
}
