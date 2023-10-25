# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['NgsbitsMappingqcLoadTest::test_load 1'] = [
    '_state',
    'id',
    'sodar_uuid',
    'date_created',
    'date_modified',
    'caseqc_id',
    'sample',
    'region_name',
    'records'
]

snapshots['NgsbitsMappingqcLoadTest::test_load 2'] = {
    'records': [
        GenericRepr("NgsbitsMappingqcRecord(key='trimmed base percentage', value=0.57)"),
        GenericRepr("NgsbitsMappingqcRecord(key='clipped base percentage', value=0.91)"),
        GenericRepr("NgsbitsMappingqcRecord(key='mapped read percentage', value=99.89)"),
        GenericRepr("NgsbitsMappingqcRecord(key='on-target read percentage', value=2.33)"),
        GenericRepr("NgsbitsMappingqcRecord(key='near-target read percentage', value=5.16)"),
        GenericRepr("NgsbitsMappingqcRecord(key='properly-paired read percentage', value=98.51)"),
        GenericRepr("NgsbitsMappingqcRecord(key='insert size', value=420.41)"),
        GenericRepr("NgsbitsMappingqcRecord(key='duplicate read percentage', value=28.37)"),
        GenericRepr("NgsbitsMappingqcRecord(key='bases usable (MB)', value=1205.26)"),
        GenericRepr("NgsbitsMappingqcRecord(key='target region read depth', value=31.29)"),
        GenericRepr("NgsbitsMappingqcRecord(key='target region 10x percentage', value=97.48)"),
        GenericRepr("NgsbitsMappingqcRecord(key='target region 20x percentage', value=94.61)"),
        GenericRepr("NgsbitsMappingqcRecord(key='target region 30x percentage', value=61.85)"),
        GenericRepr("NgsbitsMappingqcRecord(key='target region 50x percentage', value=0.97)"),
        GenericRepr("NgsbitsMappingqcRecord(key='target region 60x percentage', value=0.18)"),
        GenericRepr("NgsbitsMappingqcRecord(key='target region 100x percentage', value=0.05)"),
        GenericRepr("NgsbitsMappingqcRecord(key='target region 200x percentage', value=0.01)"),
        GenericRepr("NgsbitsMappingqcRecord(key='target region 500x percentage', value=0.0)"),
        GenericRepr("NgsbitsMappingqcRecord(key='target region half depth percentage', value=96.6)"),
        GenericRepr("NgsbitsMappingqcRecord(key='AT dropout', value=0.13)"),
        GenericRepr("NgsbitsMappingqcRecord(key='GC dropout', value=2.12)"),
        GenericRepr("NgsbitsMappingqcRecord(key='SNV allele frequency deviation', value=2.17)")
    ],
    'sample': 'sample'
}
