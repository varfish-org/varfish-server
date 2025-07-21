# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['BuildLegacyModelTest::test_build_legacy_pedigree legacy pedigree for family.yaml'] = [
    {
        'affected': 2,
        'father': 'father',
        'has_gt_entries': True,
        'mother': 'mother',
        'patient': 'index',
        'sex': 1
    },
    {
        'affected': 1,
        'father': '0',
        'has_gt_entries': True,
        'mother': '0',
        'patient': 'father',
        'sex': 1
    },
    {
        'affected': 1,
        'father': '0',
        'has_gt_entries': True,
        'mother': '0',
        'patient': 'mother',
        'sex': 2
    }
]
