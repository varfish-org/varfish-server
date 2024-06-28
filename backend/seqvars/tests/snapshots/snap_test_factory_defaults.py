# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['CreatePresetsSetTest::test_create_presetsset_short_read_exome_legacy 1'] = {
    'date_created': '2024-07-01T00:00:00Z',
    'date_modified': '2024-07-01T00:00:00Z',
    'description': "Settings for short-read exome sequencing with relaxed quality presets.  These settings are aimed at 'legacy' WES sequencing where a target coverage of >=20x cannot be achieved for a considerable portion of the exome.",
    'label': 'short-read exome sequencing (legacy)',
    'querypresetssetversion_set': [
    ],
    'rank': 3,
    'sodar_uuid': '41f60be0-7cef-4aa3-aaed-cf4a4599a084'
}

snapshots['CreatePresetsSetTest::test_create_presetsset_short_read_exome_modern 1'] = {
    'date_created': '2024-07-01T00:00:00Z',
    'date_modified': '2024-07-01T00:00:00Z',
    'description': "Settings for short-read exome sequencing with strict quality presets.  These settings are aimed at 'modern' WES sequencing where a target coverage of >=20x can be achieved for >=99% of the exome.",
    'label': 'short-read exome sequencing (modern)',
    'querypresetssetversion_set': [
    ],
    'rank': 2,
    'sodar_uuid': 'b39cfd4b-8abe-4d78-8520-10116895cea8'
}

snapshots['CreatePresetsSetTest::test_create_presetsset_short_read_genome 1'] = {
    'date_created': '2024-07-01T00:00:00Z',
    'date_modified': '2024-07-01T00:00:00Z',
    'description': 'Settings for short-read genome sequencing with strict quality presets.  These settings are aimed at WGS sequencing with at least 30x coverage.',
    'label': 'short-read genome sequencing',
    'querypresetssetversion_set': [
    ],
    'rank': 1,
    'sodar_uuid': 'c33f4584-b23b-41d8-893c-d01609de8895'
}
