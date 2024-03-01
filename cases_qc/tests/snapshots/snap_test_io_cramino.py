# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots["CraminoLoadTest::test_load 1"] = [
    "_state",
    "id",
    "sodar_uuid",
    "date_created",
    "date_modified",
    "caseqc_id",
    "sample",
    "summary",
    "chrom_counts",
]

snapshots["CraminoLoadTest::test_load 2"] = {
    "chrom_counts": [
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr1', normalized_counts=1.02)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr10', normalized_counts=1.02)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr11', normalized_counts=1.02)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr12', normalized_counts=1.01)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr13', normalized_counts=0.85)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr14', normalized_counts=0.83)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr15', normalized_counts=0.84)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr16', normalized_counts=1.03)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr17', normalized_counts=1.06)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr18', normalized_counts=0.98)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr19', normalized_counts=1.04)"
        ),
        GenericRepr("CraminoChromNormalizedCountsRecord(chrom_name='chr2', normalized_counts=1.0)"),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr20', normalized_counts=1.09)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr21', normalized_counts=0.92)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr22', normalized_counts=0.8)"
        ),
        GenericRepr("CraminoChromNormalizedCountsRecord(chrom_name='chr3', normalized_counts=1.0)"),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr4', normalized_counts=0.99)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr5', normalized_counts=0.99)"
        ),
        GenericRepr("CraminoChromNormalizedCountsRecord(chrom_name='chr6', normalized_counts=1.0)"),
        GenericRepr("CraminoChromNormalizedCountsRecord(chrom_name='chr7', normalized_counts=1.0)"),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr8', normalized_counts=0.99)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chr9', normalized_counts=0.94)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chrEBV', normalized_counts=23.65)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chrMT', normalized_counts=333.16)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chrX', normalized_counts=0.95)"
        ),
        GenericRepr(
            "CraminoChromNormalizedCountsRecord(chrom_name='chrY', normalized_counts=0.04)"
        ),
    ],
    "sample": "sample",
    "summary": [
        GenericRepr("CraminoSummaryRecord(key='File name', value='NA12878.bam')"),
        GenericRepr("CraminoSummaryRecord(key='Number of reads', value=41169470)"),
        GenericRepr("CraminoSummaryRecord(key='Yield [Gb]', value=199)"),
        GenericRepr("CraminoSummaryRecord(key='Mean coverage', value=64)"),
        GenericRepr("CraminoSummaryRecord(key='Yield [Gb] (>25kb)', value=12)"),
        GenericRepr("CraminoSummaryRecord(key='N50', value=9723)"),
        GenericRepr("CraminoSummaryRecord(key='N75', value=3929)"),
        GenericRepr("CraminoSummaryRecord(key='Median length', value=2713)"),
        GenericRepr("CraminoSummaryRecord(key='Mean length', value=4854)"),
        GenericRepr("CraminoSummaryRecord(key='Median identity', value=98)"),
        GenericRepr("CraminoSummaryRecord(key='Mean identity', value=97)"),
        GenericRepr("CraminoSummaryRecord(key='Path', value='/path/to/NA12878.bam')"),
        GenericRepr("CraminoSummaryRecord(key='Creation time', value='24/04/2023 20:51:37')"),
        GenericRepr(
            "CraminoSummaryRecord(key='Checksum', value='45EBB3BBD5DABA01A7997558DDF81429')"
        ),
    ],
}
