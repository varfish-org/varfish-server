# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots[
    "TestWritePedigreeAsPlink::testRun PLINK ped file"
] = """FAM\tindividual-0\t0\t0\t1\t2
"""
