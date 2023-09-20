"""Code for reading samtoools-style QC files into ``cases_qc.models`` records.

This includes support for bcftools stats files as well.
"""


class BcftoolsStatsParser:
    """Helper for parsing a ``bcftools stats`` output file."""
