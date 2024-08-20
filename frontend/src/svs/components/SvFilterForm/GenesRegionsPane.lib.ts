/** Regular expression for validating a genomic region. */
export const regexRegion = new RegExp(
  '^' + // start
    '(?<chrom>(chr)?' + // open chrom
    '(1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|X|Y|M|MT)' + // chrom name
    ')' + // close chrom
    '(:(?<start>(\\d+(,\\d+)*))-(?<stop>(\\d+(,\\d+)*)))?' + // optional range
    '$', // end
)
