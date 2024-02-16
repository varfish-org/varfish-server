import {
  SeqvarImpl,
  type Seqvar,
} from '@bihealth/reev-frontend-lib/lib/genomicVars'

/**
 * Seqvar as commonly used on APIs.
 */
export interface Seqvar$Api {
  release: 'GRCh37' | 'GRCh38'
  chromosome: string
  start: number
  end: number
  reference: string
  alternative: string
}

/**
 * Seqvar ACMG rating as returned by the API.
 */
export interface AcmgRating$Api extends Seqvar$Api {
  sodar_uuid: string | null
  pvs1: number
  ps1: number
  ps2: number
  ps3: number
  ps4: number
  pm1: number
  pm2: number
  pm3: number
  pm4: number
  pm5: number
  pm6: number
  pp1: number
  pp2: number
  pp3: number
  pp4: number
  pp5: number
  ba1: number
  bs1: number
  bs2: number
  bs3: number
  bs4: number
  bp1: number
  bp2: number
  bp3: number
  bp4: number
  bp5: number
  bp6: number
  bp7: number
  class_override: number | null
  class_auto: string | null
}

/**
 * Seqvar ACMG rating to be used internally.
 */
export interface AcmgRating extends Seqvar {
  sodarUuid?: string
  pvs1: number
  ps1: number
  ps2: number
  ps3: number
  ps4: number
  pm1: number
  pm2: number
  pm3: number
  pm4: number
  pm5: number
  pm6: number
  pp1: number
  pp2: number
  pp3: number
  pp4: number
  pp5: number
  ba1: number
  bs1: number
  bs2: number
  bs3: number
  bs4: number
  bp1: number
  bp2: number
  bp3: number
  bp4: number
  bp5: number
  bp6: number
  bp7: number
  classOverride?: number
  classAuto?: string
}

/**
 * Helper class to transform between `AcmgRating` and `AcmgRating$Api`.
 */
export class AcmgRating$Type {
  /**
   * Convert from API JSON to internal representation.
   *
   * @param json JSON from API
   * @returns internal representation
   */
  fromJson(json: AcmgRating$Api): AcmgRating {
    return {
      ...new SeqvarImpl(
        json.release === 'GRCh37' ? 'grch37' : 'grch38',
        json.chromosome,
        json.start,
        json.reference,
        json.alternative,
      ),
      sodarUuid: json.sodar_uuid ?? undefined,
      pvs1: json.pvs1,
      ps1: json.ps1,
      ps2: json.ps2,
      ps3: json.ps3,
      ps4: json.ps4,
      pm1: json.pm1,
      pm2: json.pm2,
      pm3: json.pm3,
      pm4: json.pm4,
      pm5: json.pm5,
      pm6: json.pm6,
      pp1: json.pp1,
      pp2: json.pp2,
      pp3: json.pp3,
      pp4: json.pp4,
      pp5: json.pp5,
      ba1: json.ba1,
      bs1: json.bs1,
      bs2: json.bs2,
      bs3: json.bs3,
      bs4: json.bs4,
      bp1: json.bp1,
      bp2: json.bp2,
      bp3: json.bp3,
      bp4: json.bp4,
      bp5: json.bp5,
      bp6: json.bp6,
      bp7: json.bp7,
      classOverride: json.class_override ?? undefined,
      classAuto: json.class_auto ?? undefined,
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
      release: obj.genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38',
      chromosome: obj.chrom,
      start: obj.pos,
      end: obj.pos + obj.del.length - 1,
      reference: obj.del,
      alternative: obj.ins,
      sodar_uuid: obj.sodarUuid ?? null,
      pvs1: obj.pvs1,
      ps1: obj.ps1,
      ps2: obj.ps2,
      ps3: obj.ps3,
      ps4: obj.ps4,
      pm1: obj.pm1,
      pm2: obj.pm2,
      pm3: obj.pm3,
      pm4: obj.pm4,
      pm5: obj.pm5,
      pm6: obj.pm6,
      pp1: obj.pp1,
      pp2: obj.pp2,
      pp3: obj.pp3,
      pp4: obj.pp4,
      pp5: obj.pp5,
      ba1: obj.ba1,
      bs1: obj.bs1,
      bs2: obj.bs2,
      bs3: obj.bs3,
      bs4: obj.bs4,
      bp1: obj.bp1,
      bp2: obj.bp2,
      bp3: obj.bp3,
      bp4: obj.bp4,
      bp5: obj.bp5,
      bp6: obj.bp6,
      bp7: obj.bp7,
      class_override: obj.classOverride ?? null,
      class_auto: obj.classAuto ?? null,
    }
  }
}

/**
 * Helper instance for converting between `AcmgRating` and `AcmgRating$Api`.
 */
export const AcmgRating = new AcmgRating$Type()

/**
 * Return whether values equal on the seqvar fields.
 *
 * Ignores the `userRepr` field.
 */
export function seqvarEqual(lhs: Seqvar, rhs: Seqvar): boolean {
  return (
    lhs.genomeBuild === rhs.genomeBuild &&
    lhs.chrom === rhs.chrom &&
    lhs.pos === rhs.pos &&
    lhs.del === rhs.del &&
    lhs.ins === rhs.ins
  )
}
