# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["CaseQcRetrieveApiViewTest::test_retrieve_existing 1"] = {
    "bcftools_statsmetrics": [],
    "case": "141cb881-d97e-4675-b501-9f62f42eed07",
    "cramino_metrics": [],
    "date_created": "2012-01-14T12:00:01Z",
    "date_modified": "2012-01-14T12:00:01Z",
    "dragen_cnvmetrics": [],
    "dragen_fragmentlengthhistograms": [],
    "dragen_mappingmetrics": [],
    "dragen_ploidyestimationmetrics": [],
    "dragen_regioncoveragemetrics": [],
    "dragen_regionfinehist": [],
    "dragen_regionhist": [],
    "dragen_regionoverallmeancov": [],
    "dragen_rohmetrics": [],
    "dragen_svmetrics": [],
    "dragen_timemetrics": [],
    "dragen_trimmermetrics": [],
    "dragen_vchethomratiometrics": [],
    "dragen_vcmetrics": [],
    "dragen_wgscontigmeancovmetrics": [],
    "dragen_wgscoveragemetrics": [],
    "dragen_wgsfinehist": [],
    "dragen_wgshist": [],
    "dragen_wgsoverallmeancov": [
        {
            "caseqc": "00000000-0000-4000-8000-000000000000",
            "date_created": "2012-01-14T12:00:01Z",
            "date_modified": "2012-01-14T12:00:01Z",
            "metrics": [
                {
                    "entry": "word1",
                    "name": "word2",
                    "section": "word0",
                    "value": 42,
                    "value_float": 3.14,
                }
            ],
            "sample": "index_000-N1-DNA1-WES1",
            "sodar_uuid": "00000000-0000-4000-8000-000000000001",
        }
    ],
    "ngsbits_mappingqcmetrics": [],
    "samtools_flagstatmetrics": [],
    "samtools_idxstatsmetrics": [],
    "samtools_statsmainmetrics": [],
    "samtools_statssupplementarymetrics": [],
    "sodar_uuid": "00000000-0000-4000-8000-000000000000",
    "state": "ACTIVE",
}
