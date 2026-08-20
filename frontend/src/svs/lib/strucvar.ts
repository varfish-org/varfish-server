import {
  BreakendStrucvarImpl,
  InsertionStrucvarImpl,
  LinearStrucvarImpl,
  Strucvar,
} from '@bihealth/reev-frontend-lib/lib/genomicVars'

/** The fields of an SV query result row that describe the variant's position. */
export interface StrucvarResultRow {
  release: string
  chromosome: string
  /**
   * Chromosome of the second end.  The column is nullable in the database, but the
   * query path always populates it; for linear variants it equals `chromosome`.
   */
  chromosome2: string
  start: number
  /** End position, on `chromosome2` for breakends and on `chromosome` otherwise. */
  end: number
  sv_type: string
}

/** Strip the `chr` prefix, which GRCh38 chromosome names carry and GRCh37 ones do not. */
const stripChr = (chromosome: string): string =>
  chromosome.startsWith('chr') ? chromosome.slice(3) : chromosome

/**
 * Build the `Strucvar` described by the given SV query result row.
 *
 * @param row The result row to convert.
 * @returns the structural variant the row describes
 */
export const strucvarFromResultRow = (row: StrucvarResultRow): Strucvar => {
  const genomeBuild = row.release === 'GRCh37' ? 'grch37' : 'grch38'
  const chrom = stripChr(row.chromosome)
  if (row.sv_type === 'BND') {
    return new BreakendStrucvarImpl(
      genomeBuild,
      chrom,
      stripChr(row.chromosome2),
      row.start,
      row.end,
    )
  } else if (row.sv_type === 'INS') {
    return new InsertionStrucvarImpl(genomeBuild, chrom, row.start)
  } else {
    return new LinearStrucvarImpl(
      row.sv_type as 'DEL' | 'DUP' | 'INV',
      genomeBuild,
      chrom,
      row.start,
      row.end,
    )
  }
}
