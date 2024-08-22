import {
  type LinearStrucvar,
  LinearStrucvarImpl,
  Strucvar,
} from '@bihealth/reev-frontend-lib/lib/genomicVars'

export type QuickPresets = any
export type InheritancePresets = any
export type CategoryPresets = any
export type QuerySettingsShortcuts = any
export type CaseSvQuery = any
export type SvQueryResultSet = any
export type SvQueryResultRow = any
export type SvComment = any
export type SvFlags = any
export type SvAcmgRating = any

/**
 * Encode the list arguments.
 */
export interface ListArgs {
  pageNo: number
  pageSize: number
  orderBy?: string
  orderDir?: string
  queryString?: string
}

export interface Strucvar$Api {
  release: string
  chromosome: string
  start: number
  end: number
  sv_type: string
  sv_sub_type: string
}

export interface AcmgRatingPage$Api {
  next: string | null
  previous: string | null
  results: AcmgRating$Api[]
}

export interface AcmgRating$Api extends Strucvar$Api {
  sodar_uuid: string | null
  class_override: number | null
}

/**
 * Seqvar ACMG rating to be used internally.
 */
export interface AcmgRating extends LinearStrucvar {
  sodarUuid?: string
  classOverride?: number
}

/**
 * Returns whether the two `AcmgRating` objects have the same rating.
 *
 * Effectively, this will only compare the categories and `classOverrides`.
 *
 * @param lhs left-hand side
 * @param rhs right-hand side
 */
export function acmgRatingEqual(lhs: AcmgRating, rhs: AcmgRating): boolean {
  const keys = ['classOverride'] as const
  return keys.every((key) => lhs[key] === rhs[key])
}

export class AcmgRating$Type {
  /**
   * Convert from API JSON to internal representation.
   *
   * @param json JSON from API
   * @returns internal representation
   */
  fromJson(json: AcmgRating$Api): AcmgRating {
    let sv_type: 'DEL' | 'DUP' | 'INV'
    if (
      json.sv_type === 'DEL' ||
      json.sv_type === 'DUP' ||
      json.sv_type === 'INV'
    ) {
      sv_type = json.sv_type
    } else {
      throw new Error(`Unknown sv_type: ${json.sv_type}`)
    }
    return {
      ...new LinearStrucvarImpl(
        sv_type,
        json.release === 'GRCh37' ? 'grch37' : 'grch38',
        json.chromosome,
        json.start,
        json.end,
      ),
      sodarUuid: json.sodar_uuid ?? undefined,
      classOverride: json.class_override ?? undefined,
    }
  }

  /**
   * Convert from internal representation to API JSON.
   *
   * @param obj internal represetation
   * @returns JSON for API
   */
  toJson(obj: AcmgRating): AcmgRating$Api {
    return {
      sodar_uuid: obj.sodarUuid ?? null,
      release: obj.genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38',
      chromosome: obj.chrom,
      start: obj.start,
      end: obj.stop,
      sv_type: obj.svType,
      sv_sub_type: obj.svType, // cheating here
      class_override: obj.classOverride ?? null,
    }
  }
}

export const AcmgRating = new AcmgRating$Type()

/**
 * Assign `Seqvar` data from object complying to `Seqvar` interface to another.
 *
 * @param lhs receiving object
 * @param rhs source object
 */
export function strucvarAssign(lhs: LinearStrucvar, rhs: LinearStrucvar): void {
  lhs.genomeBuild = rhs.genomeBuild
  lhs.chrom = rhs.chrom
  lhs.start = rhs.start
  lhs.stop = rhs.stop
  lhs.svType = rhs.svType
}

export function strucvarEqual(
  lhs: LinearStrucvar,
  rhs: LinearStrucvar,
): boolean {
  return (
    lhs.genomeBuild === rhs.genomeBuild &&
    lhs.chrom === rhs.chrom &&
    lhs.start === rhs.start &&
    lhs.stop === rhs.stop &&
    lhs.svType === rhs.svType
  )
}
