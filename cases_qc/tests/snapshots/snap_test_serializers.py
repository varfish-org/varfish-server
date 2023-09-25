# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['SerializerTest::test_load_00 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000001')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'keys': [
        37,
        40,
        41
    ],
    'sample': 'index_000-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000000',
    'values': [
        1,
        100,
        101
    ]
}

snapshots['SerializerTest::test_load_01 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000003')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word1',
            'name': 'word2',
            'section': 'word0',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'sodar_uuid': '00000000-0000-4000-8000-000000000002'
}

snapshots['SerializerTest::test_load_02 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000005')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word4',
            'name': 'word5',
            'section': 'word3',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'sample': 'index_002-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000004'
}

snapshots['SerializerTest::test_load_03 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000007')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word7',
            'name': 'word8',
            'section': 'word6',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'sample': 'index_003-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000006'
}

snapshots['SerializerTest::test_load_04 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000009')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word10',
            'name': 'word11',
            'section': 'word9',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'region_name': '',
    'sample': 'index_004-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000008'
}

snapshots['SerializerTest::test_load_05 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000011')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'keys': [
        37,
        40,
        41
    ],
    'region_name': 'word12',
    'sample': 'index_005-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000010',
    'values': [
        1,
        100,
        101
    ]
}

snapshots['SerializerTest::test_load_06 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000013')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word14',
            'name': 'word15',
            'section': 'word13',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'region_name': '',
    'sample': 'index_006-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000012'
}

snapshots['SerializerTest::test_load_07 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000015')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word17',
            'name': 'word18',
            'section': 'word16',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'region_name': '',
    'sample': 'index_007-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000014'
}

snapshots['SerializerTest::test_load_08 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000017')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word20',
            'name': 'word21',
            'section': 'word19',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'sample': 'index_008-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000016'
}

snapshots['SerializerTest::test_load_09 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000019')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word23',
            'name': 'word24',
            'section': 'word22',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'sodar_uuid': '00000000-0000-4000-8000-000000000018'
}

snapshots['SerializerTest::test_load_10 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000021')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word26',
            'name': 'word27',
            'section': 'word25',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'sodar_uuid': '00000000-0000-4000-8000-000000000020'
}

snapshots['SerializerTest::test_load_11 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000023')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word29',
            'name': 'word30',
            'section': 'word28',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'sample': 'index_011-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000022'
}

snapshots['SerializerTest::test_load_12 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000025')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word32',
            'name': 'word33',
            'section': 'word31',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'sample': 'index_012-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000024'
}

snapshots['SerializerTest::test_load_13 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000027')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word35',
            'name': 'word36',
            'section': 'word34',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'sodar_uuid': '00000000-0000-4000-8000-000000000026'
}

snapshots['SerializerTest::test_load_14 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000029')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'contig_len': 12345,
            'contig_name': 'word37',
            'cov': 3.0
        }
    ],
    'sample': 'index_014-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000028'
}

snapshots['SerializerTest::test_load_15 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000031')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word39',
            'name': 'word40',
            'section': 'word38',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'sample': 'index_015-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000030'
}

snapshots['SerializerTest::test_load_16 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000033')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'keys': [
        37,
        40,
        41
    ],
    'sample': 'index_016-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000032',
    'values': [
        1,
        100,
        101
    ]
}

snapshots['SerializerTest::test_load_17 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000035')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'keys': [
        'PCT of bases in wgs with coverage [100x:inf)',
        'PCT of bases in wgs with coverage [50x:100x)'
    ],
    'sample': 'index_017-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000034',
    'values': [
        0.21,
        26.83
    ]
}

snapshots['SerializerTest::test_load_18 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000037')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'metrics': [
        {
            'entry': 'word42',
            'name': 'word43',
            'section': 'word41',
            'value': 42,
            'value_float': 3.14
        }
    ],
    'sample': 'index_018-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000036'
}

snapshots['SerializerTest::test_load_19 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000039')"),
    'chk': [
        {
            'qualities_crc32': 'word47',
            'read_names_crc32': 'word45',
            'sequences_crc32': 'word46'
        }
    ],
    'cov': [
        {
            'count': 0,
            'value': 0
        }
    ],
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'fbc': [
        {
            'cycle': 0,
            'percentages': [
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
                0.6
            ]
        }
    ],
    'ffq': [
        {
            'counts': [
                0
            ],
            'cycle': 0
        }
    ],
    'frl': [
        {
            'count': 1,
            'value': 1
        }
    ],
    'gcd': [
        {
            'dp_percentile_10': 0.0,
            'dp_percentile_25': 0.0,
            'dp_percentile_50': 0.0,
            'dp_percentile_75': 0.0,
            'dp_percentile_90': 0.0,
            'gc_content': 0.0,
            'unique_seq_percentiles': 0.0
        }
    ],
    'idd': [
        {
            'dels': 0,
            'ins': 0,
            'length': 0
        }
    ],
    'isize': [
        {
            'insert_size': 0,
            'pairs_inward': 0,
            'pairs_other': 0,
            'pairs_outward': 0,
            'pairs_total': 0
        }
    ],
    'lbc': [
        {
            'cycle': 1,
            'percentages': [
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
                0.6
            ]
        }
    ],
    'lfq': [
        {
            'counts': [
                1
            ],
            'cycle': 1
        }
    ],
    'lrl': [
        {
            'count': 2,
            'value': 2
        }
    ],
    'sample': 'index_019-N1-DNA1-WES1',
    'sn': [
        {
            'key': 'word44',
            'value': 0
        }
    ],
    'sodar_uuid': '00000000-0000-4000-8000-000000000038'
}

snapshots['SerializerTest::test_load_20 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000041')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'gcc': [
        {
            'cycle': 2,
            'percentages': [
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
                0.6
            ]
        }
    ],
    'gcf': [
        {
            'count': 0,
            'gc_content': 0.0
        }
    ],
    'gcl': [
        {
            'count': 1,
            'gc_content': 0.1
        }
    ],
    'gct': [
        {
            'cycle': 3,
            'percentages': [
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
                0.6
            ]
        }
    ],
    'ic': [
        {
            'cycle': 0,
            'dels_fwd': 0,
            'dels_rev': 0,
            'ins_fwd': 0,
            'ins_rev': 0
        }
    ],
    'mapq': [
        {
            'count': 4,
            'value': 4
        }
    ],
    'rl': [
        {
            'count': 3,
            'value': 3
        }
    ],
    'sample': 'index_020-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000040'
}

snapshots['SerializerTest::test_load_21 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000043')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'qc_fail': {
        'duplicates': 1,
        'duplicates_primary': 1,
        'fragment_first': 1,
        'fragment_last': 1,
        'mapped': 1,
        'mapped_primary': 1,
        'paired': 1,
        'primary': 1,
        'properly_paired': 1,
        'secondary': 1,
        'singletons': 1,
        'supplementary': 1,
        'total': 1,
        'with_itself_and_mate_mapped': 1,
        'with_mate_mapped_to_different_chr': 1,
        'with_mate_mapped_to_different_chr_mapq5': 1
    },
    'qc_pass': {
        'duplicates': 0,
        'duplicates_primary': 0,
        'fragment_first': 0,
        'fragment_last': 0,
        'mapped': 0,
        'mapped_primary': 0,
        'paired': 0,
        'primary': 0,
        'properly_paired': 0,
        'secondary': 0,
        'singletons': 0,
        'supplementary': 0,
        'total': 0,
        'with_itself_and_mate_mapped': 0,
        'with_mate_mapped_to_different_chr': 0,
        'with_mate_mapped_to_different_chr_mapq5': 0
    },
    'sample': 'index_021-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000042'
}

snapshots['SerializerTest::test_load_22 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000045')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'records': [
        {
            'contig_len': 0,
            'contig_name': 'word48',
            'mapped': 0,
            'unmapped': 0
        }
    ],
    'sample': 'index_022-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000044'
}

snapshots['SerializerTest::test_load_23 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000047')"),
    'chrom_counts': [
        {
            'chrom_name': 'word50',
            'normalized_counts': 0.0
        }
    ],
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'sample': 'index_023-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000046',
    'summary': [
        {
            'key': 'word49',
            'value': 0
        }
    ]
}

snapshots['SerializerTest::test_load_24 1'] = {
    'caseqc': GenericRepr("UUID('00000000-0000-4000-8000-000000000049')"),
    'date_created': '2012-01-14T12:00:01Z',
    'date_modified': '2012-01-14T12:00:01Z',
    'records': [
        {
            'key': 'word51',
            'value': 0.0
        }
    ],
    'region_name': 'WGS',
    'sample': 'index_024-N1-DNA1-WES1',
    'sodar_uuid': '00000000-0000-4000-8000-000000000048'
}
