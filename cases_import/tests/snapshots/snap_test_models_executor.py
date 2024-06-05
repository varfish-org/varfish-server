# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["ImportCreateWithStrucvarsVcfTest::test_run external files"] = [
    {
        "available": None,
        "designation": "variant_calls",
        "file_attributes": {
            "checksum": "sha256:4042c2afa59f24a327b3852bfcd0d8d991499d9c4eb81e7a7efe8d081e66af82",
            "designation": "variant_calls",
            "genomebuild": "grch37",
            "mimetype": "text/plain+x-bgzip+x-variant-call-format",
            "variant_type": "strucvars",
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "file://cases_import/tests/data/sample-brca1.vcf.gz",
    },
    {
        "available": None,
        "designation": "variant_calls",
        "file_attributes": {
            "checksum": "sha256:6b137335b7803623c3389424e7b64d704fb1c9f3f55792db2916d312e2da27ef",
            "designation": "variant_calls",
            "genomebuild": "grch37",
            "mimetype": "application/octet-stream+x-tabix-tbi-index",
            "variant_type": "strucvars",
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "application/octet-stream+x-tabix-tbi-index",
        "path": "file://cases_import/tests/data/sample-brca1.vcf.gz.tbi",
    },
]

snapshots["ImportCreateWithStrucvarsVcfTest::test_run internal files"] = [
    {
        "checksum": None,
        "designation": "variant_calls/strucvars/orig-copy",
        "file_attributes": {
            "checksum": "sha256:4042c2afa59f24a327b3852bfcd0d8d991499d9c4eb81e7a7efe8d081e66af82",
            "designation": "variant_calls",
            "genomebuild": "grch37",
            "mimetype": "text/plain+x-bgzip+x-variant-call-format",
            "variant_type": "strucvars",
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/strucvars/external-copy-0.vcf.gz",
    },
    {
        "checksum": None,
        "designation": "variant_calls/strucvars/ingested-vcf",
        "file_attributes": {},
        "identifier_map": {},
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/strucvars/ingested.vcf.gz",
    },
    {
        "checksum": None,
        "designation": "variant_calls/strucvars/ingested-tbi",
        "file_attributes": {},
        "identifier_map": {},
        "mimetype": "application/octet-stream+x-tabix-tbi-index",
        "path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/strucvars/ingested.vcf.gz.tbi",
    },
]
